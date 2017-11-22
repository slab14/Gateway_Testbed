# Goal: Create simple controller for v0 demo (1 device to container, change policy)

# TODO:
# - Get-FSM_DAG
# -- Read file with FSM -> DAG
# - Setup-flow
# -- Take output from Get-FSM_DAG, create corresponding dataplane
# - Transition
# -- tear down existing flow, setup new flow based upon transition in FSM
# - Clean-up
# -- Clear flows setup

# - Rx_Container
# -- Process messages from containers (to call transitions)
# - Update-FSM_DAG
# -- recognize updates to "policy" and update accordingly
