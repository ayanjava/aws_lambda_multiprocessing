import time
import concurrent.futures
import boto3
from multiprocessing import Process, Pipe, Pool
import multiprocessing

logs = boto3.client('logs')

def describe_log_groups():
    print('start...')
    paginator = logs.get_paginator('describe_log_groups')
    for page in paginator.paginate():
        for log_groups in (page['logGroups']):
           yield log_groups
            
def describe_subscription_filter(loggroupname):
    print('In Subscription Filters')
    response = logs.describe_subscription_filters(logGroupName=loggroupname)['subscriptionFilters']
    print(response)
    if response:
        for log in response:
            print(log['destinationArn'])
    else:
        print("No filter")
    
def lambda_handler(event, context):
    t1 = time.perf_counter()
    loggroups_list = describe_log_groups()
    processes = []
    for loggroup in loggroups_list:
        #describe_subscription_filter(loggroup['logGroupName'])
        process = Process(target=describe_subscription_filter, args=(loggroup['logGroupName'],))
        processes.append(process)

        # start all processes
    for process in processes:
        process.start()

        # make sure that all processes have finished
    for process in processes:
        process.join()
    t2 = time.perf_counter()
    print(f'Finished in {t2-t1} seconds')
