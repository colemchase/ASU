# CSE543 Fuzz Them All Project

Local staging area for the pwn.college Fuzz Them All deliverables.

## Layout

- `fuzzer`: executable Python mutation fuzzer.
- `deliverables/level_inputs/lvN.txt`: per-level test program/writeup text.
- `deliverables/level_inputs/lvN.crash`: exact crashing input for each level.
- `report.md`: source document for the final report.

## Running the fuzzer

Inside pwn.college:

```sh
./fuzzer
```

Against another target:

```sh
FUZZ_TARGET=/path/to/program ./fuzzer
```

or:

```sh
./fuzzer /path/to/program
```
