import utils as u
import os
from time import localtime, strftime
import numpy as np
import random
import matplotlib.pyplot as plt

def get_all_repos_from_org(organization_name, startswith_text=''):
    should_look_for_more_projects = True
    page = 1
    project_list = []

    while(should_look_for_more_projects):
        link = u.github_projects_from_organization_link(organization_name, page)

        projects = u.make_request(link)

        if 'message' in projects:
            if projects['message'] == 'Not Found':
                print("Looks like {0} is not an organization. Maybe you typed the wrong name.".format(organization_name))
                exit(0)

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
        link = u.github_issues_link(organization_name, project_name, page)

        issues = u.make_request(link)

        for issue in issues:
            comments = u.make_request(link=issue['comments_url'])

            issue['created_at'] = u.get_datetime_object(issue['created_at'])
            
            if(week_number is None):
                week_number = u.get_week_number(issue['created_at'])

            number_of_commented_chars = 0

            for comment in comments:
                string = comment['body']
                number_of_commented_chars += len(string)

            if(u.get_week_number(issue['created_at']) is week_number):
                all_issues[index].append(issue)
                all_comments[index]['total'] += len(comments)
                all_comments[index]['total_len'] += number_of_commented_chars
            else:
                week_number = u.get_week_number(issue['created_at'])
                
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

def generate_reports(organization_name, project, base_dir, weeks, issues_per_week, comments_per_week, comment_avg_len_per_week, comments_len_per_week, formatted_issues_per_user_per_week, issues_per_user):

    f = open(base_dir + '{}.txt'.format(project), 'w')

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

    u.save_graph(
        x_values=weeks,
        x_label="Weeks",
        y_values=issues_per_week,
        y_label="Number of issues",
        title="Issues open per week",
        line_label="Number of issues",
        line_color="b",
        save_path=base_dir + '{}-issues_per_week.pdf'.format(project)
    )

    u.save_graph(
        x_values=weeks,
        x_label="Weeks",
        y_values=comments_per_week,
        y_label="Number of comments",
        title="Comments made per week",
        line_label="Number of comments",
        line_color="r",
        save_path=base_dir + '{}-comments_per_week.pdf'.format(project)
    )

    u.save_graph(
        x_values=weeks,
        x_label="Weeks",
        y_values=comment_avg_len_per_week,
        y_label="Average comment size",
        title="Average comment size per week",
        line_label="Total comments size",
        line_color="g",
        save_path=base_dir + '{}-comment_avg_len_per_week.pdf'.format(project)
    )

    u.save_graph(
        x_values=weeks,
        x_label="Weeks",
        y_values=comments_len_per_week,
        y_label="Total comments size",
        title="Total comments size per week",
        line_label="Total comments size",
        line_color="k",
        save_path=base_dir + '{}-total_commented_chars_per_week.pdf'.format(project)
    )

    u.save_box_graph(
        x_values=np.arange(len(issues_per_user)),
        bar_values=[issues_per_user[author] for author in issues_per_user],
        bar_labels=issues_per_user, 
        y_label='Number of issues', 
        title='Issues opened per user', 
        save_path=base_dir + '{}-issues_opened_per_user.pdf'.format(project)
    )

    colorset = set()

    lastint = 0
    while(len(colorset) < len(formatted_issues_per_user_per_week)):
        rand = random.randint(0, 0xFFFFFF)
        if abs(rand - lastint) < 10:
            rand += 10
        lastint = rand
        colorset.add("#" + "%06x" % rand)

    colorset = list(colorset)

    u.save_multiline_graph(
        x_values_list=[weeks] * len(formatted_issues_per_user_per_week),
        x_label="Weeks",
        y_values_list=[formatted_issues_per_user_per_week[author]['x'] for author in formatted_issues_per_user_per_week],
        y_label="Number of issues",
        title="Issues opened per user over time",
        line_label_list=list(formatted_issues_per_user_per_week),
        line_color_list=colorset,
        save_path=base_dir + '{}-issues_opened_per_user_over_time.pdf'.format(project)
    )

def fetch_organization_metrics(organizations, startswith_text=''):
    for organization_name in organizations:
        projects = get_all_repos_from_org(organization_name, startswith_text=startswith_text)

        if not os.path.exists('{0}'.format(organization_name)):
                os.makedirs('{0}'.format(organization_name))

        base_dir = '{0}/'.format(organization_name)
        
        for project in projects:
            print('{0}/{1} Report'.format(organization_name, project))
            print(strftime("%a, %d %b %Y %X", localtime()))
            print('-'*50, end='\n\n')

            result = fetch_metrics(project, organization_name)

            issues = result['issues']
            comments = result['comments']

            week_index = 1

            issues_per_week = []
            issues_per_user_per_week = []
            issues_per_user = {}
            comments_per_week = []
            comment_avg_len_per_week = []
            comments_len_per_week = []

            if not os.path.exists(base_dir + '{0}'.format(project)):
                os.makedirs(base_dir + '{0}'.format(project))

            for sprint_issues in issues:
                issues_per_week.append(len(sprint_issues))
                issues_per_user_per_week.append({})
                for issue in sprint_issues:
                    if issue['user']['login'] in issues_per_user:
                        issues_per_user[issue['user']['login']] += 1
                    else:
                        issues_per_user[issue['user']['login']] = 1

                    if issue['user']['login'] in issues_per_user_per_week[-1]:
                        issues_per_user_per_week[-1][issue['user']['login']] += 1
                    else:
                        issues_per_user_per_week[-1][issue['user']['login']] = 1

            formatted_issues_per_user_per_week = {}
            for author in issues_per_user:
                formatted_issues_per_user_per_week[author] = {}
                for sprint_data in issues_per_user_per_week:
                    if not 'x' in formatted_issues_per_user_per_week[author]:
                        formatted_issues_per_user_per_week[author]['x'] = []

                    if author in sprint_data:
                        formatted_issues_per_user_per_week[author]['x'].append(sprint_data[author])
                    else:
                        formatted_issues_per_user_per_week[author]['x'].append(0)

            for each in comments:
                comments_per_week.append(each['total'])
                comment_avg_len_per_week.append(each['avg_len'])
                comments_len_per_week.append(each['total_len'])

            weeks = np.linspace(1, len(issues), len(issues))

            base_dir_proj = base_dir + project + '/'

            generate_reports(organization_name, project, base_dir_proj, weeks, issues_per_week, comments_per_week, comment_avg_len_per_week, comments_len_per_week, formatted_issues_per_user_per_week, issues_per_user)

organizations = [os.environ.get('GITHUB_ORGANIZATION', '')]

fetch_organization_metrics(organizations, startswith_text=os.environ.get('STARTS_WITH_TEXT', ''))
        