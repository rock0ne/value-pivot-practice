#!/bin/bash
# Run under WSL: bash tools/run_go_rust.sh   (builds into a temp folder; no network)
# Needs Go at /root/.local/go and Rust (with clippy) at /root/.local/rust, or on PATH.
cd "$(dirname "$0")/.."
ROOT=$(pwd)
T=$(mktemp -d)
export PATH=/root/.local/go/bin:/root/.local/rust/cargo/bin:$PATH
export RUSTUP_HOME=${RUSTUP_HOME:-/root/.local/rust/rustup} CARGO_HOME=${CARGO_HOME:-/root/.local/rust/cargo}
export GOTOOLCHAIN=local GOPROXY=off GOFLAGS=-mod=mod GOCACHE=$T/gocache GOPATH=$T/gopath CARGO_NET_OFFLINE=true
go version
rustc --version
echo "--- go project (go.mod: go 1.21)"
(cd project/go-meterd && go run . 2>&1)
echo "--- go project tests"
(cd project/go-meterd && go test ./... 2>&1 | sed 's/\t[0-9.]*s$//')
echo "--- go vet on project"
(cd project/go-meterd && go vet ./... 2>&1 && echo "vet: no findings")
echo "--- same project, go.mod changed to go 1.22"
cp -r project/go-meterd $T/g122 && sed -i 's/^go 1.21$/go 1.22/' $T/g122/go.mod
(cd $T/g122 && go run . 2>&1 | grep polled)
echo "--- go answer key"
(cd answer-key/go-meterd && go run . 2>&1 && go test ./... 2>&1 | sed 's/\t[0-9.]*s$//')
for d in project answer-key; do
  cp -r $d/rust-billing $T/rb-$d
done
echo "--- rust project tests (debug)"
(cd $T/rb-project && cargo test -q --target-dir $T/target-p 2>&1 | grep -E '^test result')
echo "--- rust project, debug build"
(cd $T/rb-project && cargo run -q --target-dir $T/target-p 2>&1 | grep -E 'amount due|panicked|attempt to|slot' )
echo "--- rust project, release build"
(cd $T/rb-project && cargo run -q --release --target-dir $T/target-p 2>&1 | grep -E 'amount due|panicked|attempt to|slot')
echo "--- rust project, release build with overflow-checks on"
(cd $T/rb-project && CARGO_PROFILE_RELEASE_OVERFLOW_CHECKS=true cargo run -q --release --target-dir $T/target-c 2>&1 | grep -E 'amount due|attempt to')
echo "--- clippy on project (cast lint enabled)"
(cd $T/rb-project && cargo clippy -q --target-dir $T/target-p -- -W clippy::cast_possible_truncation 2>&1 | grep -E '^(warning|error)' | sort -u)
echo "--- rust answer key tests and release run"
(cd $T/rb-answer-key && cargo test -q --target-dir $T/target-a 2>&1 | grep -E '^test result' && cargo run -q --release --target-dir $T/target-a 2>&1)
rm -rf "$T"
