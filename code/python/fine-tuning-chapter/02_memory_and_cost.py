"""Memory and cost arithmetic for fine-tuning a 7B decoder (standard library only).

Architecture is a Llama-2-7B-shaped model: hidden 4096, 32 layers, MLP 11008,
vocabulary 32000, untied embedding and output matrices. Numbers are
illustrative planning figures, not measurements.

Run: python 02_memory_and_cost.py
"""
GB = 1e9
d, L, ffn, V = 4096, 32, 11008, 32000

attn = 4 * d * d
mlp = 3 * d * ffn
norms = 2 * d
per_layer = attn + mlp + norms
total = L * per_layer + 2 * V * d + d
print(f"per-layer params = {per_layer:,}")
print(f"total params     = {total:,} ({total / 1e9:.2f}B)")

# Full fine-tuning with mixed precision and AdamW.
w16 = 2 * total          # bf16 weights
g16 = 2 * total          # bf16 gradients
master = 4 * total       # fp32 master weights
adam = 8 * total         # fp32 m and v
full = w16 + g16 + master + adam
print("\nFull fine-tuning, mixed precision AdamW (16 bytes per parameter):")
print(f"  weights bf16 {w16 / GB:.1f} GB, grads bf16 {g16 / GB:.1f} GB, "
      f"fp32 master {master / GB:.1f} GB, Adam m+v {adam / GB:.1f} GB")
print(f"  total before activations = {full / GB:.1f} GB")

# LoRA on all linear layers.
def lora_params(r):
    per_attn = 4 * r * (d + d)
    per_mlp = 3 * r * (d + ffn)
    return L * (per_attn + per_mlp)

for r in (8, 16, 64):
    p = lora_params(r)
    print(f"\nLoRA r={r}: trainable = {p:,} ({100 * p / total:.2f}% of base)")
    adapter_state = p * (4 + 4 + 4 + 4)   # fp32 weights, grads, Adam m, v
    lora_total = w16 + adapter_state
    print(f"  LoRA bf16 base: {w16 / GB:.1f} GB + adapter state "
          f"{adapter_state / GB:.2f} GB = {lora_total / GB:.1f} GB")
    # QLoRA: base in NF4 (0.5 byte) plus double-quantized constants.
    block1, block2 = 64, 256
    c_bits = 8 / block1 + 32 / (block1 * block2)   # bits per parameter of constants
    nf4_bytes = total * (4 + c_bits) / 8
    q_total = nf4_bytes + adapter_state
    print(f"  QLoRA NF4 base: {nf4_bytes / GB:.2f} GB (constants {c_bits:.3f} bits/param) "
          f"+ adapter state {adapter_state / GB:.2f} GB = {q_total / GB:.1f} GB")

# Activation memory estimate (no checkpointing), per Korthikanti et al. style:
# roughly 34 * s * b * h bytes per layer for bf16 without attention score storage.
s_len, b = 2048, 4
act_per_layer = 34 * s_len * b * d
print(f"\nActivations s={s_len}, b={b}: ~{act_per_layer * L / GB:.1f} GB without "
      f"checkpointing, ~{(2 * s_len * b * d * L) / GB:.2f} GB layer inputs with "
      f"full recompute")

# GPU-hours and dollars: training FLOPs ~ 6 * params * tokens (full), ~4 * for LoRA
# (no weight gradients for the frozen matrices, forward + activation grads only
# is about 4 * N, plus recompute if checkpointing).
tokens = 50_000 * 600          # 50k examples x 600 tokens
epochs = 3
tok_total = tokens * epochs
flops_full = 6 * total * tok_total
flops_lora = 4 * total * tok_total
peak, mfu = 989e12, 0.35        # H100 bf16 dense peak, assumed utilisation
for name, f in (("full", flops_full), ("LoRA", flops_lora)):
    hours = f / (peak * mfu) / 3600
    print(f"\n{name}: {tok_total / 1e6:.0f}M tokens, {f:.2e} FLOPs -> "
          f"{hours:.1f} GPU-hours at MFU {mfu:.2f}; at $3/GPU-hour = ${hours * 3:.0f}")
