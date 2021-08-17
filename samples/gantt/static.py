import matplotlib.pyplot as plt


# dummy data:
# - job number
# - machine number
# - task properties: (job id, machine id, start time, duration)
num_job, num_machine = 2, 3
tasks = [(0,2,0,10), (0,1,10,5), (0,0,35,20), (1,0,15,15),(1,1,40,15), (1,2,50,10)]

# create two subplots: job view and machine view
fig, (gnt_job, gnt_machine) = plt.subplots(2,1, sharex=True)

# title
fig.suptitle('Gantt Chart', fontweight='bold')

# axis style for job subplot
job_ids = range(num_job)
gnt_job.set(ylabel='Job', \
    yticks=job_ids, \
    yticklabels=[f'Job-{i}' for i in job_ids])
gnt_job.grid(which='major', axis='x', linestyle='--')

# axis style for machine subplot
machine_ids = range(num_machine)
gnt_machine.set(xlabel='Time', ylabel='Machine',\
    yticks=machine_ids, \
    yticklabels=[f'M-{i}' for i in machine_ids])
gnt_machine.grid(which='major', axis='x', linestyle='--')

# plot each task
for (jid,mid,start,duration) in tasks:
    gnt_job.barh(jid, duration, left=start, height=0.5)
    gnt_machine.barh(mid, duration, left=start, height=0.5)

plt.show()