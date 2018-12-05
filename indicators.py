import requests
import json
from time import gmtime, strftime
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

def get_all_repos_from_org(organizationName, startswith_text=''):
    should_look_for_more_projects = True
    page = 1
    project_list = []

    while(should_look_for_more_projects):
        link = 'https://api.github.com/orgs/' + organizationName + '/repos?per_page=100&page=' + str(page)

        token = os.environ.get('GITHUB_TOKEN', '')

        r = requests.get(link, auth=('', token))

        json_data = json.loads(r.text)

        for project in json_data:
            if project['name'].startswith(startswith_text):
                project_list.append(project['name'])

        if(len(json_data) is 0):
            should_look_for_more_projects = False
        else:
            page+=1

    return project_list

def getStats(projectName, organizationName):

    should_look_for_more_projects = True
    page = 1
    all_data = [[]]
    all_comments = [{'total': 0, 'avg_len':0, 'total_len':0}]
    all_data_index = 0
    all_data_week = -1

    while(should_look_for_more_projects):
        link = 'https://api.github.com/repos/' + organizationName + '/' + projectName + '/issues?state=all&filter=all&per_page=100&page=' + str(page)

        token = os.environ.get('GITHUB_TOKEN', '')

        r = requests.get(link, auth=('', token))

        json_data = json.loads(r.text)

        for each in json_data:
            c = requests.get(each['comments_url'], auth=('', token))
            comments = json.loads(c.text)
            each['created_at'] = datetime_object = datetime.strptime(each['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if(all_data_week is -1):
                all_data_week = each['created_at'].isocalendar()[1]

            total_len_all_comments = 0
            for comment in comments:
                string = comment['body']
                total_len_all_comments += len(string)

            if(each['created_at'].isocalendar()[1] is all_data_week):
                all_data[all_data_index].append(each)
                all_comments[all_data_index]['total'] += len(comments)
                all_comments[all_data_index]['total_len'] += total_len_all_comments

            else:
                all_data_week = each['created_at'].isocalendar()[1]
                try:
                    all_comments[all_data_index]['avg_len'] = all_comments[all_data_index]['total_len']/all_comments[all_data_index]['total']
                except ZeroDivisionError:
                    all_comments[all_data_index]['avg_len'] = 0.0
                all_data_index += 1
                all_data.append([each])
                all_comments.append({'total': len(comments), 'avg_len':0, 'total_len':total_len_all_comments})

        if(len(json_data) is 0):
            should_look_for_more_projects = False
        else:
            page+=1

    return {'issues':all_data[::-1], 'comments':all_comments[::-1]}

organizations = ['fga-eps-mds', 'RolesFGA', 'integra-vendas', 'CarDefense', 'Kalkuli', 'BotLino', 'NaturalSearch', 'PDF2CASH']

for organizationName in organizations:
    projects = get_all_repos_from_org(organizationName, startswith_text='2018.2')

    if not os.path.exists('{0}'.format(organizationName)):
            os.makedirs('{0}'.format(organizationName))

    base_dir = '{0}/'.format(organizationName)
    
    for project in projects:
        print('{0}/{1} Report'.format(organizationName, project))
        print(strftime("%a, %d %b %Y %X", gmtime()))
        print('-'*50, end='\n\n')

        result = getStats(project, organizationName)

        all_data = result['issues']
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

        for each in all_data:
            issues_per_week.append(len(each))

        for each in comments:
            comments_per_week.append(each['total'])
            comment_avg_len_per_week.append(each['avg_len'])
            comments_len_per_week.append(each['total_len'])

        weeks = np.linspace(1, len(all_data), len(all_data))

        print('{0}/{1} Report'.format(organizationName, project), file=f)
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

        plt.plot(weeks, issues_per_week, 'b', label='Number of issues')
        plt.title("Issues open per week")
        plt.xlabel("Weeks")
        plt.ylabel("Number of issues")
        plt.legend()
        # plt.show()
        plt.savefig(base_dir_proj + '{}-issues_per_week.pdf'.format(project), bbox_inches='tight')
        plt.clf()

        plt.plot(weeks, comments_per_week, 'r', label='Number of comments')
        plt.title("Comments made per week")
        plt.xlabel("Weeks")
        plt.ylabel("Number of comments")
        plt.legend()
        # plt.show()
        plt.savefig(base_dir_proj + '{}-comments_per_week.pdf'.format(project), bbox_inches='tight')
        plt.clf()

        plt.plot(weeks, comment_avg_len_per_week, 'g', label='Comment avg size')
        plt.title("Average comment size per week")
        plt.xlabel("Weeks")
        plt.ylabel("Average comment size")
        plt.legend()
        # plt.show()
        plt.savefig(base_dir_proj + '{}-comment_avg_len_per_week.pdf'.format(project), bbox_inches='tight')
        plt.clf()

        plt.plot(weeks, comments_len_per_week, 'k', label='Total comments size')
        plt.title("Total comments size per week")
        plt.xlabel("Weeks")
        plt.ylabel("Total comments size")
        plt.legend()
        # plt.show()
        plt.savefig(base_dir_proj + '{}-total_commented_chars_per_week.pdf'.format(project), bbox_inches='tight')
        plt.clf()
