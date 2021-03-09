#!/usr/bin/env bash

# Uses `pf` to get pipeline status for JUNO lanes.  Writes the status data to a
# CSV file which is then copied to an OpenStack instance running the Monocle service.
#
# See https://gitlab.internal.sanger.ac.uk/sanger-pathogens/monocle/pathpipe

juno_project_id="2273"
pf_command="status -t study -i ${juno_project_id}"
# list of instances to which the CSV file should be pushed:
# only pushing to development instance ATM
scp_destinations="ubuntu@monocle_vm.dev.pam.sanger.ac.uk:pipeline_data/juno.csv"
# scp_destinations="ubuntu@monocle_vm.dev.pam.sanger.ac.uk:pipeline_data/juno.csv ubuntu@monocle_vm.pam.sanger.ac.uk:pipeline_data/juno.csv"
ssh_id="${HOME}/.ssh/id_rsa_monocle_scp"
temp_file="juno.tmp.csv"

module load -s pf/1.0.1
pf ${pf_command} --no-progress-bars -o "${temp_file}" 2>&1 | grep -v '^Wrote status information to'
for this_destination in ${scp_destinations}; do
   scp -i "${ssh_id}" -q "${temp_file}" "${this_destination}"
done
rm -f "${temp_file}"
