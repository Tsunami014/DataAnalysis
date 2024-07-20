function run_task(task, update_func) {
    // Check if task is already running
    fetch("status/"+task).then(resp => {
        data = resp.json().then(function(data) {
            if (data.State == 'FINISHED' || data.State == 'ERROR' || data.State == 'NONEXISTANT') {
                // send a POST request to start background job
                fetch('/'+task,{method: "POST"}).then(request => {
                    var upd = function() {
                        // send GET request to status URL
                        fetch("status/"+task).then(resp => {
                            data = resp.json().then(function(data) {
                                var cont = update_func(data);
                                if (cont && data.State != 'FINISHED' && data.state != 'ERROR') {
                                    // rerun in 1 second
                                    setTimeout(upd, 1000);
                                }
                            })
                        });
                    };
                    upd();
                });
            } else {
                alert('The task is already running');
            }
        });
    });
}
