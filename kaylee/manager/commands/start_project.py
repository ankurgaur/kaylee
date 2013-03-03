import os
import re
import argparse
import shutil
from jinja2 import Template
from kaylee.manager import LocalCommand


class StartProjectCommand(LocalCommand):
    name = 'startproject'
    help = 'Starts new Kaylee project'

    args = {
        'name' : {},
        ('-m', '--mode') : dict(choices=['manual', 'auto'], default='auto'),
    }

    @staticmethod
    def execute(opts):
        validate_name(opts)
        start_project(opts)


def validate_name(opts):
    if re.match(r'^\w+$', opts.name) is None:
        raise ValueError('Invalid project name: {} ([A-Za-z0-9_])'
                         .format(opts.name))


def start_project(opts):
    PROJECT_TEMPLATE_DIR = 'templates/project_template'
    PROJECT_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__),
                                         PROJECT_TEMPLATE_DIR)
    TEMPLATE_FILES = [
        #(template file in PROJECT_TEMPLATE_DIR,
        # destination file name with {project} macro replacement)
        # e.g. ('client/project.coffee', 'client/{project_name}.coffee'),

        ('client/project.coffee', 'client/{project_name}.coffee'),
        ('__init__.py', '__init__.py'),
        ('project.py', '{project_name}.py'),
    ]

    # build rendering environment constants
    project_file_name = opts.name.lower()

    # copy project template to cwd
    dest_path = os.path.join(os.getcwd(), project_file_name)
    shutil.copytree(PROJECT_TEMPLATE_PATH, dest_path)

    render_args = {
        'project_file_name' : project_file_name,
        'project_class_name' : (opts.name[0].upper() + opts.name[1:]),
        'project_mode' : expand_project_mode_opt(opts.mode),
    }

    for fname, out_fname_template in TEMPLATE_FILES:
        # render template
        template_path = os.path.join(dest_path, fname)
        with open(template_path) as f:
            template_data = f.read()
        document_data = Template(template_data).render(**render_args)

        # remove the template file
        os.remove(template_path)

        # write to output file
        out_fname = out_fname_template.format(project_name=project_file_name)
        out_path = os.path.join(dest_path, out_fname)
        with open(out_path, 'w') as f:
            f.write(document_data)

    print('Kaylee project "{}" has been successfully started.'.format(
            opts.name))


def expand_project_mode_opt(opt):
    if opt == 'manual':
        return 'MANUAL_PROJECT_MODE'
    elif opt == 'auto':
        return 'AUTO_PROJECT_MODE'
    else:
        raise ValueError('Invalid project mode option: {}'.format(opt))