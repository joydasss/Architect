"""Illustrative cost, memory, and latency arithmetic for GAN serving and training (CH11).
Standard library only. Every input below is an ASSUMPTION chosen to make the
arithmetic easy to follow. Replace each with a measurement from your own hardware.
"""

print("1. Training memory for a GAN with Adam (fp32 master weights)")
g_params = 30e6
d_params = 28e6
bytes_per_param_train = 4 + 4 + 8  # weights + gradients + two Adam moments
train_bytes = (g_params + d_params) * bytes_per_param_train
ema_bytes = g_params * 4
print("   G %.0fM params, D %.0fM params" % (g_params / 1e6, d_params / 1e6))
print("   weights+grads+Adam: %.0f MB, EMA copy of G: %.0f MB, total %.0f MB (activations excluded)"
      % (train_bytes / 1e6, ema_bytes / 1e6, (train_bytes + ema_bytes) / 1e6))

print("2. Serving cost per million images: one-pass GAN vs iterative sampler")
gpu_hour_usd = 2.50        # assumption
effective_tflops = 40.0    # assumption: sustained, not peak
gan_gflops_per_image = 40.0          # assumption: one generator pass
diffusion_gflops_per_step = 150.0    # assumption: one denoiser evaluation
steps = 25
guidance_factor = 2        # classifier-free guidance doubles the evaluations
diffusion_gflops = diffusion_gflops_per_step * steps * guidance_factor
for name, gflops in (("GAN", gan_gflops_per_image), ("diffusion", diffusion_gflops)):
    img_per_s = effective_tflops * 1e3 / gflops
    sec_per_m = 1e6 / img_per_s
    cost = sec_per_m / 3600 * gpu_hour_usd
    print("   %-9s %8.0f GFLOP/image  %8.1f images/s/GPU  GPU-hours per 1M: %6.2f  cost per 1M: $%.2f"
          % (name, gflops, img_per_s, sec_per_m / 3600, cost))
print("   ratio of compute per image: %.0fx" % (diffusion_gflops / gan_gflops_per_image))

print("3. Interactive latency budget (single image, batch 1)")
gan_ms = 15.0   # assumption
step_ms = 12.0  # assumption per denoiser evaluation at batch 1
print("   GAN one pass: %.0f ms. Diffusion %d steps x %.0f ms (guidance branches batched into one call): %.0f ms"
      % (gan_ms, steps, step_ms, steps * step_ms))

print("4. FID evaluation cost")
n_images = 50000
inception_gflops = 6.0   # assumption order of magnitude per image
total_tflop = n_images * inception_gflops / 1e3
print("   %d images x %.1f GFLOP = %.0f TFLOP, about %.0f s at %.0f TFLOPS sustained"
      % (n_images, inception_gflops, total_tflop, total_tflop / effective_tflops, effective_tflops))

print("5. Training budget in 'images shown to the discriminator'")
kimg_per_s = 0.04   # assumption: thousands of images per second on one 8-GPU node
total_kimg = 25000  # assumption: 25 million images shown
seconds = total_kimg / kimg_per_s
print("   %d kimg at %.2f kimg/s = %.1f days on this node; at $%.2f/GPU-hour with 8 GPUs: $%.0f"
      % (total_kimg, kimg_per_s, seconds / 86400, gpu_hour_usd, seconds / 3600 * 8 * gpu_hour_usd))
