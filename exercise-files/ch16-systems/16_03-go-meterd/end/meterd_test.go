package main

import (
	"slices"
	"testing"
)

func TestRejectsNegative(t *testing.T) {
	if err := Accept(Reading{"M-1", -1}); err == nil {
		t.Fatal("negative reading accepted")
	}
}

// The test the original was missing: the success path.
func TestAcceptsValid(t *testing.T) {
	if err := Accept(Reading{"M-1", 10}); err != nil {
		t.Fatalf("valid reading refused: %v", err)
	}
}

// More than one meter, so a shared loop variable would show.
func TestPollJobsEveryMeter(t *testing.T) {
	var got []string
	for _, j := range PollJobs([]string{"M-1", "M-2", "M-3"}, func(m string) { got = append(got, m) }) {
		j()
	}
	if !slices.Equal(got, []string{"M-1", "M-2", "M-3"}) {
		t.Fatalf("got %v", got)
	}
}
