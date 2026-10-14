# P0 Hub token scope probe

Plan: `docs/implementations/2026-10-14-solo-prototypes.md`. Organisation `cassandra-chorus`; token chorus-prototypes (organisation permission repo.contribute.write only; checked by the guard); run 2026-10-14T05:13:01Z.

| Step | Expected | Result | Detail |
|---|---|---|---|
| create_private_repo | success | ok | https://huggingface.co/cassandra-chorus/proto-scope-probe |
| repo_is_private | success | ok | True |
| upload_file | success | ok | 2595ae5478c1522b17af4489e598ec6bb8577257 |
| list_files | success | ok | ['.gitattributes', 'probe.txt'] |
| read_back | success | ok | probe |
| create_branch | success | ok | created |
| commit_with_current_parent | success | ok | 0e0e811e7777f3e3c9a3ba1fbc6851b6375b8ba3 |
| commit_with_stale_parent | failure | failed | HfHubHTTPError 412: Client error '412 Precondition Failed' for url 'https://huggingface.co/api/models/cassandra-chorus/proto-scope-probe/com |
| delete_repo | success | ok | deleted |
| create_private_bucket | success | ok | BucketUrl(url='https://huggingface.co/buckets/cassandra-chorus/proto-bucket-prob |
| bucket_add_file | success | ok | None |
| bucket_list | success | ok | ["BucketFile(type='file', path='probe/probe.txt', size=6, xet_hash='a999038aac71 |
| bucket_info | success | ok | BucketInfo(id='cassandra-chorus/proto-bucket-probe', private=True, created_at=da |
| delete_bucket | success | ok | deleted |
| create_repo_in_personal_namespace | failure | failed | HfHubHTTPError 403: (Request ID: Root=1-6acf0f5c-0a57e6d169f48e1b6baaba3e;05c12c5f-14df-45d3-a74b-1e38dd6a2bec) |

All steps as expected: **yes**.
