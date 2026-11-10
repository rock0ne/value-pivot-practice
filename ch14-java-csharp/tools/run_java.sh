#!/bin/bash
J=/root/.local/jdk21/bin/java
cd "$(dirname "$0")/.."
$J -version 2>&1 | head -1
$J project/java/Billing.java
$J answer-key/BillingFixed.java
