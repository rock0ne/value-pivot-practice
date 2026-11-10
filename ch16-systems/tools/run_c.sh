#!/bin/bash
# Run under WSL: bash tools/run_c.sh   (builds into a temp folder)
set -e
cd "$(dirname "$0")/.."
T=$(mktemp -d)
gcc --version | head -1
ldd --version | head -1
for opt in O0 O2; do
  gcc -$opt -o $T/meter_$opt project/meter.c
  gcc -$opt -o $T/meterfix_$opt answer-key/meter_fixed.c
  echo "meter -$opt: $($T/meter_$opt 2147483000 1000)"
  echo "meter_fixed -$opt: $($T/meterfix_$opt 2147483000 1000)"
done
gcc -O2 -fsanitize=undefined -o $T/meter_ubsan project/meter.c
echo "meter -O2 ubsan: $($T/meter_ubsan 2147483000 1000 2>&1 | tr '\n' ' ')"
for opt in O0 O2; do
  gcc -$opt -S -o $T/login_$opt.s project/login.c
  gcc -$opt -S -o $T/loginfix_$opt.s answer-key/login_fixed.c
  echo "login -$opt: wipe calls=$(grep -cE 'call\s+memset|rep stos|movaps|movdqa|pxor|movq\s+\$0|movups' $T/login_$opt.s || true) memset_calls=$(grep -c 'memset' $T/login_$opt.s || true)"
  echo "login_fixed -$opt: explicit_bzero calls=$(grep -c 'explicit_bzero' $T/loginfix_$opt.s || true)"
done
echo "--- login -O2 assembly (body)"
sed -n '/^login:/,/\.cfi_endproc/p' $T/login_O2.s | grep -vE '^\s*\.cfi' 
rm -rf $T
