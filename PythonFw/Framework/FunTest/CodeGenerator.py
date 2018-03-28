__author__ = 'david.hewitt'
import os
from FunTest.AddFolder import get_path_root


def write_template(template_name, output_path,  generated_file_name, replacement_dictionary):
    with open(os.path.join(get_path_root(), 'Template', template_name + '.template')) as fp_in:
        template = fp_in.read()

    result = template % replacement_dictionary
    with open(os.path.join(output_path, generated_file_name + ".py"), "wt") as fp_out:
            fp_out.write(result)


def format_transform_list(column_name_list):
    body = ["'" + column_name + "': None," for column_name in column_name_list]
    body.sort()
    padding = '\n' + ' ' * 16
    return padding + padding.join(body)