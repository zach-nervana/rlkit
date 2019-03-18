import run_kubernetes

if __name__ == '__main__':
    run_kubernetes.delete_jobs()
    run_kubernetes.delete_pods('rlkit')
