"""Output sizes, parameter counts, multiply-accumulate (MAC) counts and
receptive fields for convolutional networks.

Standard library only. Run: python 01_shapes_params_flops.py

Every number quoted in the chapter sections on the output-size formula,
parameter sharing, depthwise-separable convolution, VGG-16 and ResNet-50
accounting, and receptive-field growth is printed by this script.
"""


def out_size(h, k, p=0, s=1, d=1):
    """Output length along one axis: floor((h + 2p - d(k-1) - 1) / s) + 1."""
    return (h + 2 * p - d * (k - 1) - 1) // s + 1


def conv_params(cin, cout, k, groups=1, bias=True):
    w = (cin // groups) * cout * k * k
    return w + (cout if bias else 0)


def conv_macs(cin, cout, k, hout, wout, groups=1):
    return (cin // groups) * cout * k * k * hout * wout


def receptive_fields(layers):
    """layers: list of (name, kernel, stride, dilation). Returns rows of
    (name, jump, receptive_field) using j_l = j_{l-1} S_l and
    r_l = r_{l-1} + (K_l - 1) D_l j_{l-1}."""
    j, r = 1, 1
    rows = [("input", j, r)]
    for name, k, s, d in layers:
        r = r + (k - 1) * d * j
        j = j * s
        rows.append((name, j, r))
    return rows


def section(title):
    print("\n=== " + title + " ===")


def main():
    section("Output-size formula")
    cases = [
        ("224, K=7, P=3, S=2", 224, 7, 3, 2, 1),
        ("112, K=3, P=1, S=2", 112, 3, 1, 2, 1),
        ("32, K=5, P=0, S=1 (LeNet C1)", 32, 5, 0, 1, 1),
        ("224, K=3, P=1, S=1 (same)", 224, 3, 1, 1, 1),
        ("7, K=3, P=0, S=1, D=2", 7, 3, 0, 1, 2),
        ("10, K=3, P=0, S=2 (drops a column)", 10, 3, 0, 2, 1),
        ("224, K=11, P=2, S=4 (AlexNet-style)", 224, 11, 2, 4, 1),
    ]
    for label, h, k, p, s, d in cases:
        print(f"{label:42s} -> {out_size(h, k, p, s, d)}")

    section("Dense layer versus convolution on a 224x224x3 image")
    dense = 224 * 224 * 3 * 1000 + 1000
    conv = conv_params(3, 64, 3)
    print("dense 150528 -> 1000 parameters:", dense)
    print("conv 3x3, 3 -> 64 parameters (with bias):", conv)
    print("conv MACs at 224x224 output:", conv_macs(3, 64, 3, 224, 224))
    print("dense MACs:", 224 * 224 * 3 * 1000)

    section("One 3x3 layer, 64 -> 128 channels, 56x56 output")
    print("parameters:", conv_params(64, 128, 3))
    print("MACs:", conv_macs(64, 128, 3, 56, 56))

    section("Depthwise-separable versus standard 3x3, 128 -> 128, 28x28")
    std_p = conv_params(128, 128, 3, bias=False)
    dw_p = conv_params(128, 128, 3, groups=128, bias=False)
    pw_p = conv_params(128, 128, 1, bias=False)
    std_m = conv_macs(128, 128, 3, 28, 28)
    dw_m = conv_macs(128, 128, 3, 28, 28, groups=128)
    pw_m = conv_macs(128, 128, 1, 28, 28)
    print("standard params:", std_p, " MACs:", std_m)
    print("depthwise params:", dw_p, " MACs:", dw_m)
    print("pointwise params:", pw_p, " MACs:", pw_m)
    print("separable total params:", dw_p + pw_p, " MACs:", dw_m + pw_m)
    print("ratio params:", round((dw_p + pw_p) / std_p, 4),
          " formula 1/Cout + 1/K^2 =", round(1 / 128 + 1 / 9, 4))
    print("grouped conv, 4 groups, same shape params:",
          conv_params(128, 128, 3, groups=4, bias=False))

    section("1x1 bottleneck: 256 -> 64 -> 64 (3x3) -> 256 versus 3x3 256 -> 256")
    bott = (conv_params(256, 64, 1, bias=False)
            + conv_params(64, 64, 3, bias=False)
            + conv_params(64, 256, 1, bias=False))
    plain = conv_params(256, 256, 3, bias=False)
    print("bottleneck params:", bott, " plain 3x3 params:", plain,
          " ratio:", round(bott / plain, 4))

    section("VGG-16 accounting")
    cfg = [64, 64, "M", 128, 128, "M", 256, 256, 256, "M",
           512, 512, 512, "M", 512, 512, 512, "M"]
    c, hw, params, macs = 3, 224, 0, 0
    conv_params_total = 0
    for item in cfg:
        if item == "M":
            hw //= 2
        else:
            p = conv_params(c, item, 3)
            params += p
            conv_params_total += p
            macs += conv_macs(c, item, 3, hw, hw)
            c = item
    fc = [(7 * 7 * 512, 4096), (4096, 4096), (4096, 1000)]
    fc_params = sum(a * b + b for a, b in fc)
    fc_macs = sum(a * b for a, b in fc)
    print("conv parameters:", conv_params_total)
    print("fully connected parameters:", fc_params)
    print("total parameters:", params + fc_params)
    print("conv MACs:", macs, " FC MACs:", fc_macs, " total:", macs + fc_macs)
    print("FC share of parameters:", round(fc_params / (params + fc_params), 3))

    section("ResNet-50 accounting (torchvision v1.5 layout)")
    params = 7 * 7 * 3 * 64 + 2 * 64
    macs = 7 * 7 * 3 * 64 * 112 * 112
    inplanes, hw = 64, 56
    stages = [(64, 3, 1), (128, 4, 2), (256, 6, 2), (512, 3, 2)]
    for planes, blocks, stride in stages:
        for b in range(blocks):
            s = stride if b == 0 else 1
            hin = hw
            hout = hin // s
            params += inplanes * planes + 2 * planes
            macs += inplanes * planes * hin * hin
            params += 9 * planes * planes + 2 * planes
            macs += 9 * planes * planes * hout * hout
            params += planes * planes * 4 + 2 * planes * 4
            macs += planes * planes * 4 * hout * hout
            if b == 0:
                params += inplanes * planes * 4 + 2 * planes * 4
                macs += inplanes * planes * 4 * hout * hout
            inplanes = planes * 4
            hw = hout
    params += 2048 * 1000 + 1000
    macs += 2048 * 1000
    print("total parameters:", params)
    print("total MACs (convolutions + fc):", macs)

    section("Receptive field: three 3x3 stride-1 convolutions")
    for row in receptive_fields([("c1", 3, 1, 1), ("c2", 3, 1, 1), ("c3", 3, 1, 1)]):
        print(row)

    section("Receptive field: VGG-style block then pool")
    stack = [("c1", 3, 1, 1), ("c2", 3, 1, 1), ("pool1", 2, 2, 1),
             ("c3", 3, 1, 1), ("c4", 3, 1, 1), ("pool2", 2, 2, 1),
             ("c5", 3, 1, 1), ("c6", 3, 1, 1), ("c7", 3, 1, 1), ("pool3", 2, 2, 1)]
    for row in receptive_fields(stack):
        print(row)

    section("Receptive field: ResNet-50 stem and stage ends (3x3 convs only counted)")
    rn = [("conv1 7x7 s2", 7, 2, 1), ("maxpool 3x3 s2", 3, 2, 1)]
    rn += [("stage1 3x3", 3, 1, 1)] * 3
    rn += [("stage2 3x3 s2", 3, 2, 1)] + [("stage2 3x3", 3, 1, 1)] * 3
    rn += [("stage3 3x3 s2", 3, 2, 1)] + [("stage3 3x3", 3, 1, 1)] * 5
    rn += [("stage4 3x3 s2", 3, 2, 1)] + [("stage4 3x3", 3, 1, 1)] * 2
    rows = receptive_fields(rn)
    for idx in (0, 1, 2, 5, 9, 15, 16):
        print(rows[idx])
    print("final:", rows[-1])

    section("Dilated stack: 3x3 convolutions with dilation 1, 2, 4, 8")
    for row in receptive_fields([(f"d{d}", 3, 1, d) for d in (1, 2, 4, 8)]):
        print(row)

    section("Transposed convolution output: (H-1)S - 2P + D(K-1) + output_padding + 1")
    for h, k, s, p in [(7, 4, 2, 1), (14, 2, 2, 0), (7, 3, 2, 1)]:
        print(f"H={h}, K={k}, S={s}, P={p} ->", (h - 1) * s - 2 * p + (k - 1) + 1)

    section("Activation memory for one 224x224 image (fp32, 4 bytes)")
    first = 64 * 112 * 112 * 4
    print("ResNet-50 conv1 output bytes:", first, "=", round(first / 2**20, 2), "MiB")
    vgg1 = 64 * 224 * 224 * 4
    print("VGG-16 conv1_1 output bytes:", vgg1, "=", round(vgg1 / 2**20, 2), "MiB")


if __name__ == "__main__":
    main()
