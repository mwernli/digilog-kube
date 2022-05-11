# Digilog @ Kubernetes
## Run locally for testing
* install `kind` and `kubectl`.
* from the project root, run `kind create cluster --config kind-cluster-config.yaml`. This may take a few minutes.
* create the directories for the volume mounts in the newly created node:
  * login to the node by running `docker exec -it kind-control-plane bash`
  * create the directories:
    * `cd mnt`
    * `mkdir pv-1`
    * `mkdir pv-2`
    * `mkdir pv-3`
    * `mkdir pv-4`
* verify you're using the local kind context by running `kubectl config current-context`. This should display `kind-kind`.
* switch to directory `overlays/local-kind`.
* run `kubectl apply -k .` to create all kubernetes resources by kustomizing the current directory.
* run `kubectl get all` to see the status of all resources. It may take a while for all pods to be created because the images have to be downloaded to the node first. 
