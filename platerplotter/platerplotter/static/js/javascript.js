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

(function ($) {
var unique = 0;
var types = $.fn.dataTable.ext.type;
 
// Using form $.fn.dataTable.enum breaks at least YuiCompressor since enum is
// a reserved word in JavaScript
$.fn.dataTable['enum'] = function ( arr ) {
    var name = 'enum-'+(unique++);
    var lookup = window.Map ? new Map() : {};
 
    for ( var i=0, ien=arr.length ; i<ien ; i++ ) {
        lookup[ arr[i] ] = i;
    }
 
    // Add type detection
    types.detect.unshift( function ( d ) {
        return lookup[ d ] !== undefined ?
            name :
            null;
    } );
 
    // Add sorting method
    types.order[ name+'-pre' ] = function ( d ) {
        return lookup[ d ];
    };
};
})(jQuery);


$.fn.dataTable.enum( [ 'Proband', 'Family', 'Cancer Germline', 'Tumour' ] );
	$(document).ready(function() {
	    $('#dataTableReadyForPlating').DataTable({
	   		"paging": true,
	   		"order": [[ 1, "asc" ]],
	   		"processing": true,
			dom: 'lBfrtip',
	        buttons: [ {
	            extend: 'excelHtml5',
	            title: "ReadyForPlatingExport"
	        },
	        {
	            extend: 'csvHtml5',
	            title: "ReadyForPlatingExport"
	        }],
	    });
	});


$(document).ready(function() {
    $('#dataTablePag').DataTable({
   		"paging": true,
   		"processing": true,
		dom: 'lBfrtip',
        buttons: [ {
            extend: 'excelHtml5',
            title: "DataExport"
        },
        {
            extend: 'csvHtml5',
            title: "DataExport"
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
