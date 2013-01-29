function progress_process_data(data, textStatus, jqXHR) {
    
    rows = data[0];
    progresses = data[1];
    
    // Make the numbers in the progress bar increase 
    var intId = setInterval(function() {
        for(var pk_prog in progresses) {
            // Check that the progress bar is active 
            if($("#progress_"+pk_prog+" .bar").length < 1) {
                continue;
            }

            // Get the width of the progress bar and translate
            // it into a text value 
            var v = parseInt($("#progress_"+pk_prog+" .bar").css('width'));
            $("#progress_"+pk_prog+" span").text(v+"%");
        }
    }, 80);

    // Animate the width of the progress bar for 1 second
    values = {}
    for(var pk in rows) {
        // If the progress bar is active 
        if(progresses[pk] != undefined && 
            $("#progress_"+pk+" .bar").length > 0) {
            $("#progress_"+pk+" .bar").animate(
                { width: progresses[pk]+"%" }, 
                { duration: 1000 }
                );
        }
    }
     
    // Update row HTML once the progress
    // bar animation is finished (1 second later) 
    setTimeout(function() {
        // Stop updating the progress bar width
        clearInterval(intId);
        for(var pk in rows) {
            $("#row_"+pk).html(rows[pk]);
        }
    }, 1000);
    
}

function progress_update() {
    return $.ajax({
        url: '/hid/ajax_progress/',
        data: {},
        success: progress_process_data
    });
}

function init() {
    setInterval(progress_update, 5000);
}

$(document).ready(init);

