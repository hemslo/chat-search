[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/chat-search)](https://artifacthub.io/packages/search?repo=chat-search)

## Usage

[Helm](https://helm.sh) must be installed to use the charts.  Please refer to
Helm's [documentation](https://helm.sh/docs) to get started.

Once Helm has been set up correctly, add the repo as follows:

    helm repo add chat-search https://hemslo.github.io/chat-search/

If you had already added this repo earlier, run `helm repo update` to retrieve
the latest versions of the packages.  You can then run `helm search repo
chat-search` to see the charts.

To install the chat-search chart:

    helm install my-chat-search chat-search/chat-search

To uninstall the chart:

    helm delete my-chat-search
