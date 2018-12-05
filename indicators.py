import requests
import json
from time import gmtime, strftime
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

token = os.environ.get('GITHUB_TOKEN', '')

def save_graph(x_values, x_label, y_values, y_label, title, line_label, line_color, save_path):
    plt.plot(x_values, y_values, line_color, label=line_label)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.savefig(save_path, bbox_inches='tight')
    plt.clf()

def make_request(link, token=token):
    r = requests.get(link, auth=('', token))
    json_data = json.loads(r.text)
    return json_data

def github_issues_link(organization_name, project_name, page):
    return 'https://api.github.com/repos/' + organization_name + '/' + project_name + '/issues?state=all&filter=all&per_page=100&page=' + str(page)

def get_datetime_object(date_string):
    return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')

def get_week_number(datetime_object):
    return datetime_object.isocalendar()[1]

def get_all_repos_from_org(organization_name, startswith_text=''):
    should_look_for_more_projects = True
    page = 1
    project_list = []

    while(should_look_for_more_projects):
        link = 'https://api.github.com/orgs/' + organization_name + '/repos?per_page=100&page=' + str(page)

        projects = make_request(link)

        for project in projects:
            if project['name'].startswith(startswith_text):
                project_list.append(project['name'])

        if(len(projects) is 0):
            should_look_for_more_projects = False
        else:
            page+=1

    return project_list

def fetch_metrics(project_name, organization_name):

    should_look_for_more_issues = True
    page = 1
    all_issues = [[]]
    all_comments = [{'total': 0, 'avg_len':0, 'total_len':0}]
    index = 0
    week_number = None

    while(should_look_for_more_issues):
        link = github_issues_link(organization_name, project_name, page)

        issues = make_request(link)

        for issue in issues:
            comments = make_request(link=issue['comments_url'])

            issue['created_at'] = get_datetime_object(issue['created_at'])
            
            if(week_number is None):
                week_number = get_week_number(issue['created_at'])

            number_of_commented_chars = 0

            for comment in comments:
                string = comment['body']
                number_of_commented_chars += len(string)

            if(get_week_number(issue['created_at']) is week_number):
                all_issues[index].append(issue)
                all_comments[index]['total'] += len(comments)
                all_comments[index]['total_len'] += number_of_commented_chars
            else:
                week_number = get_week_number(issue['created_at'])
                
                try:
                    all_comments[index]['avg_len'] = all_comments[index]['total_len']/all_comments[index]['total']
                except ZeroDivisionError:
                    all_comments[index]['avg_len'] = 0.0
                
                index += 1

                all_issues.append([issue])
                all_comments.append({'total': len(comments), 'avg_len':0, 'total_len': number_of_commented_chars})

        if(len(issues) is 0):
            should_look_for_more_issues = False
        else:
            page+=1

    return {'issues': all_issues[::-1], 'comments': all_comments[::-1]}

organizations = ['fga-eps-mds']

for organization_name in organizations:
    projects = get_all_repos_from_org(organization_name, startswith_text='2018.2')

    if not os.path.exists('{0}'.format(organization_name)):
            os.makedirs('{0}'.format(organization_name))

    base_dir = '{0}/'.format(organization_name)
    
    for project in projects:
        print('{0}/{1} Report'.format(organization_name, project))
        print(strftime("%a, %d %b %Y %X", gmtime()))
        print('-'*50, end='\n\n')

        result = fetch_metrics(project, organization_name)

        issues = result['issues']
        comments = result['comments']

        week_index = 1

        issues_per_week = []
        comments_per_week = []
        comment_avg_len_per_week = []
        comments_len_per_week = []

        if not os.path.exists(base_dir + '{0}'.format(project)):
            os.makedirs(base_dir + '{0}'.format(project))

        base_dir_proj = base_dir + project + '/'

        f = open(base_dir_proj + '{}.txt'.format(project), 'w')

        for issue in issues:
            issues_per_week.append(len(issue))

        for each in comments:
            comments_per_week.append(each['total'])
            comment_avg_len_per_week.append(each['avg_len'])
            comments_len_per_week.append(each['total_len'])

        weeks = np.linspace(1, len(issues), len(issues))

        print('{0}/{1} Report'.format(organization_name, project), file=f)
        print('-'*50, end='\n\n', file=f)
        for i in range(len(weeks)):
            print('Sprint %d: ' %(i), file=f)
            print('\tIssues: %d' %(issues_per_week[i]), file=f)
            print('\tComments: %d' %(comments_per_week[i]), file=f)
            print('\tComment avg size: %d chars' %(comment_avg_len_per_week[i]), file=f)
            print('\tTotal comment size: %d chars' %(comments_len_per_week[i]), file=f)
        print('-'*50, end='\n\n', file=f)
        print('Total issues: %d' %(sum(issues_per_week)), file=f)
        print('Total comments: %d' %(sum(comments_per_week)), file=f)

        f.close()

        save_graph(
            x_values=weeks,
            x_label="Weeks",
            y_values=issues_per_week,
            y_label="Number of issues",
            title="Issues open per week",
            line_label="Number of issues",
            line_color="b",
            save_path=base_dir_proj + '{}-issues_per_week.pdf'.format(project)
        )

        save_graph(
            x_values=weeks,
            x_label="Weeks",
            y_values=comments_per_week,
            y_label="Number of comments",
            title="Comments made per week",
            line_label="Number of comments",
            line_color="r",
            save_path=base_dir_proj + '{}-comments_per_week.pdf'.format(project)
        )

        save_graph(
            x_values=weeks,
            x_label="Weeks",
            y_values=comment_avg_len_per_week,
            y_label="Average comment size",
            title="Average comment size per week",
            line_label="Total comments size",
            line_color="g",
            save_path=base_dir_proj + '{}-comment_avg_len_per_week.pdf'.format(project)
        )

        save_graph(
            x_values=weeks,
            x_label="Weeks",
            y_values=comments_len_per_week,
            y_label="Total comments size",
            title="Total comments size per week",
            line_label="Total comments size",
            line_color="k",
            save_path=base_dir_proj + '{}-total_commented_chars_per_week.pdf'.format(project)
        )
