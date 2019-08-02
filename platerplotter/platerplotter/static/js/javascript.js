$(document).ready(function() {
    $('#dataTable').DataTable({
    	"paging": false,
	});
});

$(document).ready(function() {
    $('#dataTable2').DataTable({
    	"paging": false,
	});
});

$(document).ready(function() {
    $('#dataTablePag').DataTable({
   		"paging": true,
   		"processing": true,
		dom: 'lBfrtip',
        buttons: [ {
            extend: 'excelHtml5',
            title: "ValidationListExport"
        },
        {
            extend: 'csvHtml5',
            title: "ValidationListExport"
        }],
    });
});

function getCookie(name) {
	var cookieValue = null;
	console.log("Get Cookie")
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
var csrftoken = getCookie('csrftoken');
