$(document).ready(function() {
    var add_field = function(e) {
    	// retrieve the text entered
    	var field = e.target.value;

    	if (field != ""){
    		// gives me the 2 chr code of what block was triggered
    		var block = $(e.target).closest('div').attr('id');		
    		$("#id_" + block + "-text").attr('value', '');
    		canvas_data[block].push({});
    		var position = canvas_data[block].length - 1;
    		canvas_data[block][position]['text'] = field;		
	
    		//set default values:
    		canvas_data[block][position]['id'] = temp_id;
    		canvas_data[block][position]['colour'] = 'yl';
    		canvas_data[block][position]['note'] = '';
		
    		temp_id++;
		
    		print_field_list(canvas_data, block);
    	}
    	return false;
    };

    var print_field_list = function(data, block) {
    	$("#" + block + "-field-list").remove();
    	$("#" + block + "-fields").append("<ul id='" + block + "-field-list' class='form-field-list field-list'></ul>");
    	$.each(data[block], function(i,item){
        	/*if (item['note'] != '') {
        		$("#" + block + "-field-list").append('\n<li id=' + item.id + '> \
        													<span class="field-text"><span class="note-option ui-icon ui-icon-gear"></span>' + item.text + '</span> \
        													<span class="field-comment">' + item.note + '</span> \
        													<div class="field-control"> \
        													    <div class="colours">\
        															<span class="note-colour note-yellow"></span> \
        															<span class="note-colour note-blue"></span> \
        															<span class="note-colour note-orange"></span> \
        															<span class="note-colour note-green"></span> \
        															<span class="note-colour note-purple"></span> \
        														</div> \
        														<span class="done">Done</span> \
        														<span class="delete-note">Delete</span> \
        													</div> \
        												</li>');
	
        	} else {*/
    		$("#" + block + "-field-list").append('\n<li id=' + item.id + '> \
    													<span class="field-text"><span class="note-option ui-icon ui-icon-gear"></span>' + item.text + '</span> \
    													<span class="field-comment"></span> \
    													<div class="field-control"> \
    													    <div class="colours">\
    															<span class="note-colour note-yellow"></span> \
    															<span class="note-colour note-blue"></span> \
    															<span class="note-colour note-orange"></span> \
    															<span class="note-colour note-green"></span> \
    															<span class="note-colour note-purple"></span> \
    														</div> \
    														<span class="delete-note">Delete</span> \
    													</div> \
    												</li>');
        //	}
    		//$('#' + block + '-field-list *').disableSelection();
    		var list_item = 'li#' + item.id;
    		
    		// Apply the correct field note colour on load
    		switch (item['colour']) {
    		case "yl":
    			$(list_item).css('background-color', '#FFDF52');
    			break;
    		case "or":
    			$(list_item).css('background-color', '#F0A848');
    			break;
    		case "bl":
    			$(list_item).css('background-color', '#48A8C0');
    			break;
    		case "gr":
    			$(list_item).css('background-color', '#C0D830');
    			break;
    		case "pr":
    			$(list_item).css('background-color', '#A86090');
    			break;
    		}
    		
    		// Open Options
    		$(list_item + ' > .field-text > .note-option').click(function () {
    				$(this).closest('.field-text').nextAll('.field-control').show();
    				
    				// Replace note text with input
    				$(list_item + ' > span.field-text').after('<input id="' + item.id + '_text" class="field-text" value="' + item.text + '"/>');
    				$(list_item + ' > span.field-text').remove();
    				
    				
    				// Replace note comment with textarea
    				//$(list_item + ' > span.field-comment').after('<textarea id="' + item.id + '_comment" class="field-comment" name="field_comment">' + item.note + '</textarea>');                    
    				//$(list_item + ' > span.field-comment').remove();
    				
    				$(list_item + ' > input.field-text').keypress(function(event) {
                    	var code = event.keyCode || event.which;
                    	if (code == 13) {
                			var list = $("#" + block + "-field-list li");
                			var this_text = '#' + item.id + '_text';
                			var this_comment = '#' + item.id + '_comment';
                			var text = $(this_text).val();
                			//var note = $(this_comment).val();
            				var block = $(this_text).closest('li').closest('div').attr('id');
            				canvas_data[block][i]['text'] = text;
            				//canvas_data[block][i]['note'] = note;
                			$(list).find('.field-control').hide();
                			print_field_list(canvas_data, block);
                    	}
                    });
    		});
    		
            // Set color Blue
    		$(list_item + ' > div > div > span.note-blue').mousedown(function () {
    		    $(list_item).css('background-color','#48A8C0');
    			canvas_data[block][i]['colour'] = 'bl';
    			var this_text = '#' + item.id + '_text';
    			var text = $(this_text).val();
				canvas_data[block][i]['text'] = text;
			    print_field_list(canvas_data, block);
    		});
    		
            // Set color Yellow
    		$(list_item + ' > div > div > span.note-yellow').mousedown(function () {
    		    $(list_item).css('background-color','#FFDF52');
    			canvas_data[block][i]['colour'] = 'yl';
    			var this_text = '#' + item.id + '_text';
    			var text = $(this_text).val();
				canvas_data[block][i]['text'] = text;
			    print_field_list(canvas_data, block);
    		});
            // Set color Green
    		$(list_item + ' > div > div > span.note-green').mousedown(function () {
    		    $(list_item).css('background-color','#C0D830');
    			canvas_data[block][i]['colour'] = 'gr';
    			var this_text = '#' + item.id + '_text';
    			var text = $(this_text).val();
				canvas_data[block][i]['text'] = text;
			    print_field_list(canvas_data, block);
    		});
		    // Set color Purple
    		$(list_item + ' > div > div > span.note-purple').mousedown(function () {
    		    $(list_item).css('background-color','#A86090');
    			canvas_data[block][i]['colour'] = 'pr';
    			var this_text = '#' + item.id + '_text';
    			var text = $(this_text).val();
				canvas_data[block][i]['text'] = text;
			    print_field_list(canvas_data, block);
    		});
		    // Set color Orange
    		$(list_item + ' > div > div > span.note-orange').mousedown(function () {
    		    $(list_item).css('background-color','#F0A848');
    			canvas_data[block][i]['colour'] = 'or';
    			var this_text = '#' + item.id + '_text';
    			var text = $(this_text).val();
				canvas_data[block][i]['text'] = text;
			    print_field_list(canvas_data, block);
    		});
    		
            // Close Note Options
    		/*$(list_item + ' > div.field-control > span.done').click(function () {
    			var list = $("#" + block + "-field-list li");
    			var this_text = '#' + item.id + '_text';
    			var this_comment = '#' + item.id + '_comment';
    			var text = $(this_text).val();
    			//var note = $(this_comment).val();
				var block = $(this_text).closest('li').closest('div').attr('id');
				canvas_data[block][i]['text'] = text;
				//canvas_data[block][i]['note'] = note;
    			$(list).find('.field-control').hide();
    			print_field_list(canvas_data, block);
    		});*/
    		
    		// Click on delete note
    		$(list_item + ' > div.field-control > span.delete-note').mousedown(function () {
                // Add Dialog to confirm delete later
    			var field_id = $(this).closest('li').attr('id');
    			var block = $(this).closest('div').closest('li').closest('div').attr('id');
    			var data = { field_id:field_id, block:block };
    			$(this).closest('li').fadeOut();
    			canvas_data[block].splice(i,1);
    			print_field_list(canvas_data, block);
    		});
    	});
		// Apply Sortable
    	$("ul.form-field-list").sortable({
    		connectWith: 'ul.form-field-list',
    		//handle: $('.field-text'),
    		stop: function(e, ui) {
    			var order = $(this).sortable('toArray');
    			var block = $(this).closest('div').attr('id');
    			var sent_item = ui.item.attr('id');
    			// order is giving me the list and order of fields in the source block after a move.
    			update_sending_block(sent_item, block, order);
    		},
    		receive: function(e, ui) {
    			var order = $(this).sortable('toArray');
    			var block = $(this).closest('div').attr('id');
    			var sent_item = ui.item.attr('id');
    			var sender = ui.sender.closest('div').attr('id');	
    			// order is giving me the list and order of fields in the receiving block after a move.
    			update_receiving_block(order,block,sent_item, sender);
    		}
    	});
    }

    var update_sending_block = function(sent_item, block, order) {
    	//This should just remove the moved object from the sender block.
    	var old_canvas_data = clone(canvas_data);
	
    	canvas_data[block] = [];
	
    	var old_position = 0;
    	var new_position = 0;
	
    	for (var i in old_canvas_data[block]){
    		var id_to_check = String(old_canvas_data[block][i]['id']);
    		if (jQuery.inArray(id_to_check, order) != -1) {
			
    			for (i in old_canvas_data[block]) {
    				if (old_canvas_data[block][i]['id'] == id_to_check) {
    					old_position = i;
    				}
    			}
			
    			for (i in order) {
    				if (order[i] == id_to_check) {
    					new_position = i;
    				}
    			}
    			data_length = canvas_data[block].length;
    			canvas_data[block][new_position] = old_canvas_data[block][old_position];
    		}
    	}
    	print_field_list(canvas_data, block);
    };

    var update_receiving_block = function(order, block, sent_item, sender) {
    	var old_data = clone(canvas_data);

    	canvas_data[block] = [];

    	//This loop all to find the array position we want from old_data for our sent item	
    	for (var i in old_data[sender]) {
    		if (old_data[sender][i]['id'] == sent_item) {
    			var sent_position = i;
    		}
    	}

    	var old_position = 0;
    	// Each value in data.order is a field'd ID
    	for (var i in order) {
    		canvas_data[block].push({});
    		// If the id of the field doesn't match the ID of the sent item
    		if (order[i] != sent_item) {
    			canvas_data[block][i] = old_data[block][old_position];
    			old_position++;
    		} else {
    			// If it does, then use the sent data.
    			canvas_data[block][i] = old_data[sender][sent_position];
    		}
    	}
    	print_field_list(canvas_data, block);
    };

    var clone = function(obj){
        if(obj == null || typeof(obj) != 'object'){ 
    		return obj;
    	}
        var temp = new obj.constructor();
    	for(var key in obj) {
            temp[key] = clone(obj[key]);
    	}

    	return temp;
    }

    $('#send').click(function() {
    	var label = $('#id_canvas-label').val();
    	if (label != "") {
    		event.preventDefault();
    		var project_id = $('#project_id').text();
    		var account = $('#account').text();
	    	var private_canvas = $('#id_canvas-private_canvas').val();
    		var notes = $('#id_canvas-notes').val();
    		var tags = $('#id_canvas-tags').val();
    		$.post('/save_canvas/', { canvas_data:canvas_data, account:account, private_canvas:private_canvas, label:label, tags:tags, notes:notes, project_id:project_id}, function(data) {
    			window.location.replace(data);
    		});
    	} else {
    		$('.canvas-title').prepend("<span class='error'>Enter a canvas name.</span><br />");
    	}
    	event.preventDefault();
    });

    $('#clear').click(function() {
    	var dialog = $('<div></div>')
    		.html('All notes for this canvas will be permanently deleted. Are you sure?')
    		.dialog({
    			title: 'Delete all fields?',
    			resizable: false,
    			height:150,
    			modal: true,
    			buttons: {
    				'Delete all items': function() {
    					$(this).dialog('close');
    					var canvas_blocks = ['kp','ka','kr','vp','cr','ch','cs','co','rs'];
    					canvas_data = {'kp': [],'ka': [],'kr': [],'vp': [],'cr': [],'ch': [],'cs': [],'co': [],'rs': []};
    					canvas_blocks.forEach(function(item) {
    						print_field_list(canvas_data,item);	
    					});
    				},
    				Cancel: function() {
    					$(this).dialog('close');
    				}
    			}
    		});
    	dialog.dialog();
    });
    
    $("input[id$='id_kp-text'], \
    	input[id$='id_ka-text'], \
    	input[id$='id_kr-text'], \
    	input[id$='id_vp-text'], \
    	input[id$='id_cr-text'], \
    	input[id$='id_ch-text'], \
    	input[id$='id_cs-text'], \
    	input[id$='id_co-text'], \
        input[id$='id_rs-text']").keydown(function(e) {
    	var code = e.keyCode || e.which;
    	if (code == 13) {
         	e.preventDefault();
    		add_field(e);
    	}
    	if (code == 27) {
    	    $(e.target).attr('value', '');
    	}
    })
    .blur(function() {
        add_field()
    });
 
    // initialize var Data array assuming the view isn't passing any data
    var temp_id = 1;
    var canvas_data = {'kp': [],'ka': [],'kr': [],'vp': [],'cr': [],'ch': [],'cs': [],'co': [],'rs': []};
});