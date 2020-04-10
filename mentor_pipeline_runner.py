# import argparse
import glob
import os

import click

from mentor_pipeline.run import Pipeline
from mentor_pipeline import noise


def _get_mentors_data_root(data: os.PathLike) -> str:
    return data or os.path.join(os.path.curdir, "data", "mentors")


@click.group()
def cli():
    pass


@cli.command()
@click.option("--force-update-transcripts", default=False, is_flag=True)
@click.option("-m", "--mentor", required=True, type=str)
@click.option("-d", "--data", required=False, type=click.Path(exists=True))
def data_update(force_update_transcripts, mentor, data):
    p = Pipeline(mentor, _get_mentors_data_root(data))
    p.data_update(force_update_transcripts=bool(force_update_transcripts))


@cli.command()
@click.option(
    "-n", "--noise", "noise_sample", required=True, type=click.Path(exists=True)
)
@click.argument("files", required=True, nargs=-1, type=click.Path())
def reduce_noise(noise_sample, files):
    all_files = []
    for f in [files] if isinstance(files, str) else files:
        all_files.extend([x for x in glob.glob(f)])
    noise.reduce_noise(noise_sample, all_files)


@cli.command()
@click.option("-m", "--mentor", required=True, type=str)
@click.option("-d", "--data", required=False, type=click.Path(exists=True))
def topics_by_question_generate(mentor, data):
    p = Pipeline(mentor, _get_mentors_data_root(data))
    p.topics_by_question_generate(mentors=[mentor])


@cli.command()
@click.option("-m", "--mentor", required=True, type=str)
@click.option("-d", "--data", required=False, type=click.Path(exists=True))
def videos_reduce_noise(mentor, data):
    p = Pipeline(mentor, _get_mentors_data_root(data))
    p.videos_reduce_noise()


@cli.command()
@click.option("-m", "--mentor", required=True, type=str)
@click.option("-d", "--data", required=False, type=click.Path(exists=True))
def videos_update(mentor, data):
    p = Pipeline(mentor, _get_mentors_data_root(data))
    p.videos_update()


if __name__ == "__main__":
    cli()
