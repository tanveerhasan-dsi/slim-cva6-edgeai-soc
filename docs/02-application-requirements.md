# 02 — Application Requirements

## 1. The device

An always-on autonomous micro-UAV perception node:

- **Obstacle avoidance** from mmWave radar point clouds.
- **Airframe health monitoring** from IMU and acoustic vibration — bearing wear,
  propeller damage, motor fault.

The chip is mounted on a drone frame and evaluated in flight.

## 2. Why the application is a requirement, not decoration

Every deletion must be arguable **from the workload**. That is the point a
reviewer will press hardest, and an application chosen after the fact cannot
support the argument.

| Removal | Justification from this workload |
|---|---|
| Floating point | Models are int8/int4-quantised end to end |
| MMU / page-table walker | Flight control needs deterministic loop latency; page-walk and TLB-miss jitter are **disqualifying**, not merely unused |
| Atomics | Single hart, no SMP, no coherent memory |
| DRAM controller and PHY | Networks fit in on-chip SRAM |
| MIPI PHY | Sensor ingest is SPI-rate |

The MMU row is worth dwelling on. "Unused" is a weak argument — an unused block
is merely wasteful. "Actively harmful to the timing guarantee the product
sells" is a strong one, and it is the argument this application supports.

## 3. Why radar rather than a camera

This is the single most consequential choice in the specification, and it is a
feasibility judgement rather than a preference.

Camera-class vision on this device does not close, for two independent reasons:

- **Weights.** An INT8 MobileNetV2-SSD or Tiny-YOLO-class detector needs roughly
  3–6 MB of weights. A realistic on-chip SRAM budget for an MPW die is a few
  hundred kilobytes — an order-of-magnitude shortfall, not a tuning problem.
  Closing it requires off-chip DRAM, hence a DRAM PHY.
- **Ingest.** SPI cannot sustain a camera stream. MIPI CSI-2 requires a hard
  analogue PHY.

Both fixes are mixed-signal blocks outside the scope set in
[`01-objectives-and-scope.md`](01-objectives-and-scope.md) §4, and both have
sunk university tapeouts before.

Radar point clouds and IMU streams are low-bandwidth, SPI-friendly, and their
networks are hundreds of kilobytes. **The demonstration survives; the
infeasibility does not.**

| ID | Requirement |
|---|---|
| **R-2.1** | Primary perception input MUST be mmWave radar, with IMU and acoustic vibration as secondary inputs. |
| **R-2.2** | No design element MAY require a DRAM PHY or a MIPI PHY. |
| **R-2.3** | Sensor ingest MUST be achievable over SPI, I²C or I²S at the sensor's native rate. |

## 4. Memory

| ID | Requirement |
|---|---|
| **R-2.4** | All model weights and activations MUST reside in on-chip SRAM. |
| **R-2.5** | The SRAM budget MUST be derived from the measured footprint of the selected networks, and the derivation recorded — not chosen as a round number and defended afterwards. |
| **R-2.6** | The design MUST record measured worst-case activation working-set size, not just weight size. |

**On R-2.6.** Weight size is the number everyone quotes and the one least likely
to be the binding constraint. Peak activation working set frequently exceeds it
for convolutional layers, and discovering that after the SRAM macros are placed
is expensive.

## 5. Architecture

| ID | Requirement |
|---|---|
| **R-2.7** | The SoC MUST have a duty-cycled structure: an always-on domain running the trigger detector, and a power-gated compute domain woken on trigger. |
| **R-2.8** | The compute domain MUST comprise the pruned CVA6 and a CV-X-IF-attached TinyML datapath. |
| **R-2.9** | Peripherals MUST include SPI, I²C, UART, I²S/PDM, PWM outputs for motor control, timers, CLINT/PLIC and JTAG debug. |
| **R-2.10** | The design MUST include PMP and a secure boot ROM. |
| **R-2.11** | Power domains, clock domains and reset topology MUST be documented before RTL freeze. |

## 6. The closed-loop requirement

| ID | Requirement |
|---|---|
| **R-2.12** | The design MUST report measured **sensor-to-PWM latency**, end to end. |
| **R-2.13** | It MUST report **worst-case observed jitter** on that path, not only mean or median latency. |
| **R-2.14** | The latency budget MUST be allocated across sensor ingest, preprocessing, inference and control before RTL freeze, and the measured result compared against that allocation. |

**On R-2.13.** The argument for removing the MMU is a *determinism* argument.
An average latency figure does not evidence determinism — it is precisely the
statistic that hides the tail the MMU was blamed for. Reporting mean latency to
support a jitter claim will be read as not understanding your own thesis.

## 7. Benchmark corpus

Two corpora, serving different purposes. Both are required.

### Corpus A — portable baselines, for comparability

MLPerf Tiny v1.3+ (keyword spotting DS-CNN; visual wake words MobileNetV1
96×96; anomaly detection autoencoder on ToyADMOS; streaming wake-word 1D
DS-CNN), plus Embench-IoT and CoreMark.

These do **not** drive design decisions. They exist so results are citable
against other people's silicon. Visual wake words is retained as a *portable
benchmark* even though camera input is out of scope for the device — running a
standard workload is not the same as building for it.

### Corpus B — target workload, for the design

A radar point-cloud obstacle-detection network and an IMU/acoustic anomaly
detector, both int8-quantised and constrained to the SRAM budget, together with
the RTOS kernel, all interrupt service paths, and the flight-control loop.

| ID | Requirement |
|---|---|
| **R-2.15** | Subsetting decisions MUST be driven by Corpus B only. |
| **R-2.16** | Corpus B MUST include the RTOS kernel and every interrupt service path, not only inference code. |
| **R-2.17** | Both corpora MUST be reported. |

**On R-2.16.** Inference code is the well-behaved part of the workload and the
part everyone profiles. Boot code, fault handlers, RTOS context switches and
driver paths use instructions that inference never touches — and they are
exactly the paths where an instruction removed in error surfaces as a hang in
the field rather than a failure on the bench.

## 8. Evaluation metrics

| ID | Metric |
|---|---|
| **R-2.18** | µJ per inference, and GOPS/W |
| **R-2.19** | Inference frames-per-second against milliwatts consumed |
| **R-2.20** | Worst-case sensor-to-PWM latency and jitter |
| **R-2.21** | Area in normalised gate-equivalents |
| **R-2.22** | ISA coverage versus PPA, as a curve across configurations |
| **R-2.23** | Baselines MUST include unmodified CVA6, Ibex, and X-HEEP |

**On R-2.22.** A curve, not a point. A single configuration answers "is it
smaller"; a curve answers "what does each increment of ISA coverage cost",
which is the question the project is actually about — and it is the figure that
carries a paper.

**On R-2.23.** These baselines answer the *why not Ibex* question with data
instead of argument. Include them even if — especially if — they are
unflattering on raw area.

---

# 9. Reference architecture

## 9.1 Subtract, then reinvest

Both halves are required. Subtraction alone produces a smaller core — a
configuration change nobody needs a tapeout to demonstrate. Reinvestment alone
produces an accelerator SoC, of which there are many. The combination produces
the claim worth publishing:

> *Same die area. A large fraction of the ISA gone. Several-fold better
> inference energy. The binaries still run.*

The framing also disciplines the engineering: every removal is answerable to
"what did the reclaimed area buy", which stops the project drifting into pruning
for its own sake.

## 9.2 Block structure

```
   radar / IMU / mic
          |  SPI, I2S
          v
  +-------------------------+
  |  ALWAYS-ON DOMAIN       |   uW class, never gated
  |  front-end + trigger    |
  +-------------------------+
          | wake
          v
  +-------------------------+     CV-X-IF     +----------------------+
  |  SLIM CVA6 (CV32A6)     |<===============>|  Xtinyml datapath    |
  |  pruned to subset       |  execute stage  |  INT8/INT4 array     |
  +-------------------------+                 +----------------------+
          |                                            |
          +---------------------+----------------------+
                                v
                   +-----------------------------+
                   |  ON-CHIP SRAM  (weights,    |
                   |  activations, code, data)   |
                   +-----------------------------+
                                |
                           PWM -> motors
```

## 9.3 Why RV32, not RV64

The originating proposal specified RV64IMAC. For an address space of a few
hundred kilobytes, a 64-bit datapath, register file and ALU are pure cost — and
that cost comes out of the same budget the FPU and MMU removals were supposed to
free. Choosing RV64 spends a large part of the slimming result before pruning
begins.

RV32 for tapeout; RV64 through the same harness as a scaling study (R-1.2), so
the claim is measured rather than asserted.

## 9.4 Two removals to strike from the pitch

Both appear in almost every first draft of this project, and neither survives
contact with the source.

**Hypervisor extension.** `CVA6Cfg.RVH` defaults to `0`, is CV64-only, and is
still maturing. A default CV32 build contains none. There is no area to claim.

**"L2 coherence."** CVA6 has no L2 in the core; coherence exists only in the
OpenPiton configuration.

A reviewer who notices that half a four-item removal list removes nothing will
discount the other half.

## 9.5 What was retained from the originating proposal

See [`prior-proposal.pdf`](prior-proposal.pdf). Its concreteness is a genuine
strength and is carried into this specification:

- Named FPGA target — Kintex UltraScale+ class
- A staged validation matrix, gate by gate ([`06`](06-verification-requirements.md))
- Named custom instructions — `MAT_LOAD`, `MAT_MUL`, `MAT_ACT_RELU`
- The physical demonstration: die on a daughterboard, mounted on a drone frame,
  benchmarked as FPS against milliwatts

Its validation *metrics* are the part replaced. "Successfully run CoreMark" is a
smoke test, not a tapeout gate (R-6.1). Its camera-based sensing and RV64 target
are replaced for the feasibility reasons in §3 and §9.3.

---

**Previous:** [`01-objectives-and-scope.md`](01-objectives-and-scope.md) ·
**Next:** [`03-core-requirements.md`](03-core-requirements.md)
