# head of workflow: always the same
from urllib.parse import urlparse
from common_workflow_description.common_workflow_description import Sample, Storage, step

try:
    from pyiron_workflow import Workflow
except ImportError:
    from common_workflow_description.common_workflow_description import Workflow

from analysis_steps import calc_YoungsModulus, plot_curves

# start code
wf = Workflow('Sandia Fracture Challenge 3', automate_execution=False)         # name
proceduresLibrary = urlparse('https://raw.githubusercontent.com/SteffenBrinckmann/common-workflow-description_Procedures/main')
storage=Storage(proceduresLibrary)                                             # folder of database

# body of workflow: this changes
sample = Sample('AM_NA_05')

wf.step1 = step(storage, sample, 'metallography', {}, autorun=True)   #define step and link to storage for procedures
wf.step2 = step(storage, sample, 'light microscopy', {}, autorun=True)
wf.step3 = step(storage, sample, 'tensile test', {}, autorun=True)
wf.step4 = step(storage, sample, 'light microscopy', {}, autorun=True)
wf.step5a = step(storage, sample, 'sem', {'voltage':'30'}, autorun=True)
wf.step5b = step(storage, sample, 'sem', {'voltage':'30'}, autorun=True)

wf.step6 = plot_curves(wf.step3.outputs.y[1], 'Strain (Gauge0)', 'Engr. Stress')
wf.step7 = calc_YoungsModulus(wf.step3.outputs.y[1], 'Strain (Gauge0)', 'Engr. Stress')

wf.step1 >> wf.step2 >> wf.step3 >> wf.step4 >> wf.step5a >> wf.step5b >> wf.step6 >> wf.step7
wf.starting_nodes = [wf.step1]

# footer, always the same
print('Output:\n  ','\n   '.join([f"{k}: {v}" for k, v in list(wf.outputs.to_value_dict().items())]))
wf.draw().render(filename='io_demo_2', format='png', cleanup=True) #plot to file

# {"type":"common-workflow-description", "version":1.0, "shasum":"d5d8342b266851e28919e69039918d2c2a9ca4f2"}
