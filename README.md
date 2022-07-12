# Digilog @ Kubernetes
## Run locally for testing
### First time only
* Install [`kind`](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) and [`kubectl`](https://kubernetes.io/docs/tasks/tools/).
* From the project root, run `kind create cluster --config kind-cluster-config.yaml`. This may take a few minutes.
* Create the directories for the volume mounts in the newly created node:
  * Login to the node by running `docker exec -it kind-control-plane bash`
  * Create the directories:
    * `cd mnt`
    * `mkdir pv-1`
    * `mkdir pv-2`
    * `mkdir pv-3`
    * `mkdir pv-4`
### Subsequent runs
* Verify you're using the local kind context by running `kubectl config current-context`. This should display `kind-kind`.
* Switch to directory `overlays/local-kind`.
* Run `kubectl apply -k .` to create all kubernetes resources by kustomizing the current directory.
* Run `kubectl get all` to see the status of all resources. It may take a while for all pods to be created because the images have to be downloaded to the node first.
* You can use `kubectl delete -k .` in `overlays/local-kind` to delete everything. Do NOT use this command on the production cluster. Doublecheck that `kubectl` is configured to use the local kind cluster before issuing this command.
## Run on a production cluster
### First time only
* Install [`kubectl`](https://kubernetes.io/docs/tasks/tools/) if not already installed.
* Make sure resource limits are defined for each Pod (if required by the cluster).
* Add the remote cluster config file as `kubectl`'s config (usually stored `$HOME/.kube/config`). Note: to use separate clusters, add all configuration into the same file. `kind` will automatically augment an existing file if the `kind` cluster is set up after creating the production cluster config. See https://kubernetes.io/docs/tasks/access-application-cluster/configure-access-multiple-clusters/ for more info.
* Verify you're using the correct cluster config by executing `kubectl config current-context`. If necessary, switch to the correct context by using `kubectl config get-contexts` and `kubectl config use-context`.
* If not already present (check with `kubectl get secrets`), create the necessary secrets `postgres-secret` and `mongodb-secret` directly on the cluster. Do NOT check production secrets into version control.
### Subsequent runs
* Verify you're using the correct cluster config by executing `kubectl config current-context`.
* Switch to directory `overlays/init-k8s`.
* Run `kubectl apply -k .` to create all kubernetes resources by kustomizing the current directory.
* Run `kubectl get all` to see the status of all resources.

## Hints
* To migrate the PostgreSQL database, delete the `flyway-migrate` Job if it already exists before applying the Job (`kubectl delete job flyway-migrate`)
* To preview Kustomization results execute `kubectl kustomize /path/to/overlay -o out.yaml`
* To get individual resource files:
  * Create an up-to-date `out.yaml` file as indicated in the previous bullet
  * Create a Python virtual environment from `helpers/requirements.txt` and activate it
  * Use `python yaml_helper.py split <overlay>` to create a folder with individual resource files. These can then be applied to the cluster individually
  * These files can now be applied individually to the cluster using `kubectl apply -f <file>`
* To display the image versions of the custom `trephor` images in the `base` directory, you can use `python yaml_helper.py image-tag`
* To update the image versions of the custom `trephor` images in the `base` directory, you can use `python yaml_helper.py image-tag <version>` (e.g. `yaml_helper.py image-tag 0.3.7`)
* To show an overview of resource requests and limits, run `python yaml_helper.py summarize init-k8s`
