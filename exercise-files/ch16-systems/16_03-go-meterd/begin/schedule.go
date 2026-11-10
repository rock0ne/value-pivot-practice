package main

// PollJobs builds one job per meter. The scheduler runs the jobs later.
func PollJobs(meters []string, poll func(string)) []func() {
	var jobs []func()
	for _, m := range meters {
		jobs = append(jobs, func() { poll(m) })
	}
	return jobs
}
