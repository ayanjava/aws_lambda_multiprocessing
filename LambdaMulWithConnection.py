import time
import boto3
from multiprocessing import Process, Pipe

logs = boto3.client('logs')

def describe_log_groups():
    paginator = logs.get_paginator('describe_log_groups')
    for page in paginator.paginate():
        for log_groups in page['logGroups']:
            yield(log_groups)

def describe_subscription_filter(loggroupname,conn):
    print('In Subscription Filters')
    response = logs.describe_subscription_filters(logGroupName=loggroupname)['subscriptionFilters']
    if len(response) != 0:
        for log in response:
            print(log['destinationArn'])
        conn.send([log['destinationArn']])
    conn.close()

def lambda_handler(event, context):
    t1 = time.perf_counter()
    evlaute_loggroups = []
    processes = []
    parent_connections = []
    loggroups_list = describe_log_groups()
    for loggroup in loggroups_list:
        parent_conn, child_conn = Pipe()
        parent_connections.append(parent_conn)
        print(parent_connections)
        print(loggroup['logGroupName'])
        process = Process(target=describe_subscription_filter, args=(loggroup['logGroupName'], child_conn,))
        processes.append(process)
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    for parent_connection in parent_connections:
        print(parent_connection)
    print('done')



    t2 = time.perf_counter()
    print(f'Finished in {t2-t1} seconds')
