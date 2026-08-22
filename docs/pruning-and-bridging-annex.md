# Annex — Bridging, Worked Through

Companion to [`pruning-and-bridging.md`](pruning-and-bridging.md), which states
what pruning may remove and what guarantee replaces it. This annex is the
handler-level detail: three removals followed all the way through, and the
mistakes that spoil them.

Read the brief first — in particular
[what "the same functionality" means](pruning-and-bridging.md#2-what-the-same-functionality-means),
because everything here is an instance of that one claim.

> Illustrative throughout. The code is pseudocode for reading, not for building,
> and the examples assume the device described in
> [`objective-6-test-chip.md`](objective-6-test-chip.md): one application, one
> hart, quantised arithmetic, and a control loop with a deadline.

Each example fails in a different way, which is the reason there are three of
them:

| | Example | What it shows |
|:--:|---|---|
| **1** | [Integer division](#1-example-integer-division) | Reproducing an **arithmetic result**, edge cases included |
| **2** | [An atomic operation](#2-example-an-atomic-operation) | Reproducing a **guarantee** by a different mechanism |
| **3** | [A misaligned access](#3-example-a-misaligned-access) | Bridging a **structural** removal, not an ISA one |
| **4** | [Three ways this goes wrong](#4-three-ways-this-goes-wrong) | Where handlers break in practice |

---

## 1. Example: integer division

The clearest case. Suppose measurement shows divide and remainder are rare in
the workload, and the hardware divider is removed.

**Before pruning.** The core executes it directly:

```asm
    div  a0, a1, a2      # a0 = a1 / a2, in hardware
```

**After pruning.** The same instruction, unchanged in the binary, now traps. The
handler reconstructs the operation from the instruction word:

```c
void handle_illegal_instruction(trap_frame_t *f)
{
    uint32_t insn = faulting_instruction(f);

    if (opcode(insn) == OP && funct7(insn) == M_EXTENSION) {
        uint32_t a = f->x[rs1(insn)];        /* operands from the saved state */
        uint32_t b = f->x[rs2(insn)];
        uint32_t result;

        switch (funct3(insn)) {
        case DIV:  result = div_s(a, b);  break;
        case DIVU: result = div_u(a, b);  break;
        case REM:  result = rem_s(a, b);  break;
        case REMU: result = rem_u(a, b);  break;
        default:   escalate(f); return;
        }

        if (rd(insn) != 0)                   /* x0 stays zero, always */
            f->x[rd(insn)] = result;

        f->resume_pc += instruction_length(insn);   /* 2 or 4 — derive it */
        return;                                     /* resume the program */
    }

    escalate(f);   /* not ours: a real illegal instruction */
}
```

The division itself is an ordinary shift-and-subtract loop. What matters is that
it reproduces the **architecturally specified** answers, including the cases
that are not errors:

| Case | Specified result | Why it catches people out |
|---|---|---|
| Divide by zero | A defined value — **not** a trap | The intuitive handler raises an exception; hardware does not |
| Most-negative value ÷ −1 | Wraps to itself, quotient; remainder zero | The mathematically correct answer is unrepresentable |

Get either wrong and the pruned part is no longer a legal implementation. The
bug surfaces years later and looks like a compiler fault.

**The result:** identical. **The cost:** a trap, a save, a decode, a software
divide, a restore and a return, in place of one instruction.

---

## 2. Example: an atomic operation

A different shape: here the bridge preserves a *guarantee*, not an arithmetic
result. On a device with one hart and no other agent sharing memory, an atomic
read-modify-write only has to be indivisible with respect to interrupts.

```asm
    amoadd.w  a0, a2, (a1)     # atomically: a0 = *a1; *a1 = a0 + a2
```

```c
    uint32_t addr = f->x[rs1(insn)];
    uint32_t operand = f->x[rs2(insn)];

    uint32_t saved = disable_interrupts();      /* indivisible from here ... */
    uint32_t old = *(volatile uint32_t *)addr;
    *(volatile uint32_t *)addr = old + operand;
    restore_interrupts(saved);                  /* ... to here */

    if (rd(insn) != 0)
        f->x[rd(insn)] = old;
```

The hardware guaranteed atomicity through the memory system; the handler
guarantees it by making itself uninterruptible. **Same promise, different
mechanism** — and it holds only because of a property of this device. On a
multi-core part it would be wrong.

That is the general lesson: what a bridge is allowed to assume comes from the
system, and those assumptions have to be written down. Reserved-pair
instructions such as load-reserved and store-conditional need more care than the
simple case above, because a trap can land between the two halves.

---

## 3. Example: a misaligned access

Not every bridge covers a missing instruction. Support for loads and stores that
cross a natural alignment boundary is *optional*, and dropping it removes real
logic from the memory path.

On this device the case is easy to construct: sensor frames arrive packed, and a
field that is not naturally aligned produces a misaligned access.

```asm
    lw   a0, 3(a1)       # a1+3 is not word-aligned
```

After pruning this raises a misaligned-address exception, and the handler
performs the access as two aligned accesses and merges the halves:

```c
    uint32_t addr  = f->x[rs1(insn)] + imm(insn);
    uint32_t base  = addr & ~3u;
    uint32_t shift = (addr & 3u) * 8;        /* non-zero: an aligned access
                                                would not have trapped */
    uint32_t lo = *(volatile uint32_t *)base;
    uint32_t hi = *(volatile uint32_t *)(base + 4);

    if (rd(insn) != 0)
        f->x[rd(insn)] = (lo >> shift) | (hi << (32 - shift));

    f->resume_pc += instruction_length(insn);
```

Note what the last line is doing. The faulting instruction may be a 32-bit `lw`
**or** its 16-bit compressed form — one handler serves both widths. Advance the
resume address by a fixed four bytes and, on the compressed form, execution
resumes in the *middle* of the next instruction. It will not crash cleanly; it
decodes whatever the misaligned bytes happen to spell.

Deriving the length from the encoding rather than assuming a width is the whole
defence, which is why the division example writes `instruction_length(insn)`
instead of a constant.

Note also what this example is *not*: a second aligned access is not free, so a
routine that walks a packed frame field by field can slow down sharply even
though no instruction was removed from the ISA at all.

---

## 4. Three ways this goes wrong

### The handler needs the instruction it is emulating

If the divide handler is itself compiled with divide instructions in it — a
compiler emitting one for an innocent `%` in the handler's own code — the first
division traps into a handler that immediately divides, which traps again,
forever.

**The rule:** the emulation library is built for the *pruned* subset, and its
own instruction usage is checked against that subset. This is a build-time
guarantee, not a code-review habit.

### The handler runs inside an interrupt

After pruning, interrupt service routines contain emulated instructions too, so
the emulator can be entered while another emulation is in progress. Any shared
scratch state is then corrupted — at a rate rare enough to be effectively
undebuggable once the design is in silicon.

**The rule:** a handler is a pure function of the trap state it was handed.

### A trap inside a trap

An emulated memory access can itself fault. Rare, so usually untested, so the
one that reaches the field.

---


---

[`README`](../README.md) · [`pruning-and-bridging.md`](pruning-and-bridging.md)
