# Coleman_Chase_CSE543_Fuzz Them All Project

Name: Chase Coleman

Course: CSE543

Date: July 5, 2026

## Dependencies

The fuzzer is implemented in Python 3 and uses only Python standard library modules: `os`, `random`, `signal`, `subprocess`, and `sys`. It expects the target program to be executable at `/challenge/prog` in the pwn.college environment unless a different target is supplied with the `FUZZ_TARGET` environment variable or as the first command-line argument.

## Input Generation Strategy

The fuzzer uses mutation based input generation. It starts from a seed corpus containing empty input, small strings, integer boundary values, format string tokens, path traversal strings, repeated bytes, and selected binary byte values. For each test case, it randomly selects one seed and applies one or more mutations.

The mutation operators include bit flips, byte/string insertion, deletion, overwrite, appending interesting values, and splicing random bytes. Generated inputs are capped at 4096 bytes to avoid runaway test cases. The fuzzer executes the target with each generated input through standard input, suppresses normal output, and treats fatal signal exits and common crash exit statuses as crashes. When a crash is detected, it saves the exact input as `crash_0` for verification and submission.

## Level Notes

This submission includes solved levels 1 through 8 and level 10. Level 9 was attempted but is not included as a solved level because the fuzzer continued running without discovering a verified crashing input despite repeated attempts.

Level 1 used the mutation strategy above. The fuzzer found a 198 byte input that reliably crashed the target program. The crash was verified in pwn.college with `/challenge/challenge < crash_0`.

Level 2 reused the mutation strategy against the new target binary. The fuzzer generated long inputs containing repeated characters and numeric edge cases, then found a crashing input that reproduced under `/challenge/challenge < crash_0`.

Level 3 reused the same fuzzer. It discovered a crashing mutated byte input, saved it as `crash_0`, and the crash was verified through `/challenge/challenge`.

Level 4 reused the mutation based fuzzer and found a crashing input during randomized testing. The saved testcase reproduced the segmentation fault when submitted to `/challenge/challenge`.

Level 5 reused the same strategy against the level 5 binary. The fuzzer found a crashing testcase, saved it as `crash_0`, and verification reproduced the crash.

Level 6 reused the same fuzzer and found a larger crashing input. The testcase was saved as `crash_0` and verified with `/challenge/challenge < crash_0`.

Level 7 used the mutation based fuzzer on the level 7 target. A generated testcase triggered a segmentation fault and was verified with the challenge wrapper.

Level 8 reused the same fuzzer and found a crashing input that reproduced with `/challenge/challenge < crash_0`.

Level 9 was attempted with an argv-focused mutation strategy adapted for the target. The fuzzer performed a deterministic seed pass and then continued through mutation testing for a 10 minute run, reaching about 28,000 argv cases without producing a `crash_0` file or a verified crash. Because no crashing input was found despite repeated attempts, I could not produce an exact `.crash` file for this level.

Level 10 reused the same mutation based fuzzer. It found a crashing input that reproduced under `/challenge/challenge < crash_0`.
