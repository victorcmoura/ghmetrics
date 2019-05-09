import requests
import json
from time import gmtime, strftime
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

def get_datetime_object(date_string):
    return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')

def get_week_number(datetime_object):
    return datetime_object.isocalendar()[1]


def github_issues_link(organization_name, project_name, page):
    return 'https://api.github.com/repos/' + organization_name + '/' + project_name + '/issues?state=all&filter=all&per_page=100&page=' + str(page)

def github_projects_from_organization_link(organization_name, page):
    return 'https://api.github.com/orgs/' + organization_name + '/repos?per_page=100&page=' + str(page)

def make_request(link, token=os.environ.get('GITHUB_TOKEN', '')):
    r = requests.get(link, auth=('', token))
    json_data = json.loads(r.text)
    return json_data

def save_graph(x_values, x_label, y_values, y_label, title, line_label, line_color, save_path):
    plt.plot(x_values, y_values, line_color, label=line_label)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def save_multiline_graph(x_values_list, x_label, y_values_list, y_label, title, line_label_list, line_color_list, save_path):
    for i in range(len(line_label_list)):
        x = plt.plot(x_values_list[i], y_values_list[i], line_color_list[i], label=line_label_list[i])
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def save_box_graph(x_values, bar_values, bar_labels, y_label, title, save_path):
    fig, ax = plt.subplots()
    ax.bar(x_values, bar_values, align='center', alpha=0.5)
    plt.xticks(x_values, bar_labels)
    plt.ylabel(y_label)
    plt.title(title)
    fig.autofmt_xdate()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()