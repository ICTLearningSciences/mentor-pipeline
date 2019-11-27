## Mentor Pipeline
---------------

Use these tools to create/update a mentor for Mentorpal.

### Quick Start

#### Required Setup (session videos and timestamps)
TODO: needs to download session videos and timestamp files automatically but for now...
Download session videos and timestamps and place them under `./data/mentors/{mentor_id}/build/recordings` eg.

```
data/mentors/my_new_mentor/
├── build
│   ├── recordings
│   │   ├── session1
│   │   │   ├── p001-bio-long.csv
│   │   │   ├── p001-bio-long.mp4
│   │   │   ├── p002-some-utterances.csv
│   │   │   ├── p002-some-utterances.mp4
│   │   ├── session2
│   │   │   ├── p001-more-questions.csv
│   │   │   ├── p001-more-questions.mp4
```

#### Build and Test a Mentor

If raw video, audio and timestamp files for a mentor are stored in S3 (more on this
below), we can use the following commands to build a classifier for the mentor.
Note that videos are not required to generate a classifier to a new mentor.

##### Create/update the training data
```bash
make data/mentors/{mentor_id}
```

##### Train {mentor} classifier
```bash
make checkpoint/{mentor_id}
```

#### Run mentorpal cluster with {mentor} data and classifier
```bash
cd .. && make local-run-dev
```

### Generate web videos (if you're ready to run the website and not just classifier)
```bash
make videos/mentors/{mentor_id}
```

#### Example endpoints for mentorpal cluster
- Mentor Homepage (Test web site) `http://localhost:8080/mentorpanel/?mentor={mentor}`
- Mentor API (Test classifier, e.g. with [Postman](https://www.getpostman.com/downloads/)) `http://localhost:8080/mentor-pipeline/questions/?mentor={mentor}&query={question}`

---------------
### Pipeline Overview
The classification data pipeline can be used to create all data needed for a usable
mentor from raw recording files.

### Output
After running the pipeline the following files will be generated:
- `{mentor}/data/classifier_data.csv`
- `{mentor}/data/topics.csv`
- `{mentor}/data/utterance_data.csv`
- `videos/{mentor}/mobile/idle.mp4`
- `videos/{mentor}/web/idle.mp4`
- `videos/{mentor}/mobile/{mentor}_{video_id}.mp4`
- `videos/{mentor}/web/{mentor}_{video_id}.mp4`

### Supplementary Documentation
#### Generating Timestamp Files
After the interview is done, watch it fully and note down the start and end timestamps
for each question. Timestamp files should be in a CSV file of the following format:

| Notes    | Answer/Utterance | Question | Response start       | Response end         |
|----------|------------------|----------|----------------------|----------------------|
| (string) | (char: A/U)      | (string) | (timestamp HH:MM:SS) | (timestamp HH:MM:SS) |


Development
-----------

Any changes made to this repo should be covered by tests. To run the existing tests:

```
make test
```

All pushed commits must also pass format and lint checks. To check all required tests before a commit:

```
make test-all
```

To fix formatting issues:

```
make format
```

Releases
--------

Currently, this image is semantically versioned. When making changes that you want to test in another project, create a branch and PR and then you can release a test tag one of two ways:

To build/push a work-in-progress tag of `mentor-pipeline` for the current commit in your branch

- find the `docker_tag_commit` workflow for your commit in [circleci](https://circleci.com/gh/ICTLearningSciences/workflows/mentor-pipeline)
- approve the workflow
- this will create a tag like `https://hub.docker.com/mentor-pipeline:${COMMIT_SHA}`

To build/push a pre-release semver tag of `mentor-pipeline` for the current commit in your branch

- create a [github release](https://github.com/ICTLearningSciences/mentor-pipeline/releases/new) **from your development branch** with tag format `/^\d+\.\d+\.\d+(-[a-z\d\-.]+)?$/` (e.g. `1.0.0-alpha.1`)
- find the `docker_tag_release` workflow for your git tag in [circleci](https://circleci.com/gh/ICTLearningSciences/workflows/mentor-pipeline)
- approve the workflow
- this will create a tag like `uscictdocker/mentor-pipeline:1.0.0-alpha.1`



Once your changes are approved and merged to master, you should create a release tag in semver format as follows:

- create a [github release](https://github.com/ICTLearningSciences/mentor-pipeline/releases/new) **from master** with tag format `/^\d+\.\d+\.\d$/` (e.g. `1.0.0`)
- find the `docker_tag_release` workflow for your git tag in [circleci](https://circleci.com/gh/ICTLearningSciences/workflows/mentor-pipeline)
- approve the workflow
- this will create a tag like `uscictdocker/mentor-pipeline:1.0.0`
