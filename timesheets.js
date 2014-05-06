
function CreateTimebills(data_in) {
	// based on the sample restlet described at
	// http://blog.prolecto.com/2011/12/18/netsuite-restlet-sample-program-exploits-new-power/

	//nlapiLogExecution('DEBUG','createRecord',(typeof data_in.timebill));
	var result = new Object();
	var msg = validateTimeBills(data_in);
	if (msg) {
		result.status = "failed";
		result.message = msg;
		return result;
	}
	var timebills = data_in.timebill;
	for (var timebillobject in timebills) {
		var timebill = timebills[timebillobject];
		var trandate = timebill.trandate;
		var customer = timebill.customer;
		var casetaskevent = timebill.casetaskevent;
		var hours = timebill.hours;
		var memo = timebill.memo;
		var timebill = nlapiCreateRecord('timebill');
		timebill.setFieldValue('trandate', trandate);
		timebill.setFieldText('customer', customer);
		timebill.setFieldText('casetaskevent', casetaskevent);
		timebill.setFieldValue('memo', memo);
		timebill.setFieldValue('hours', hours);
		var timebillid = nlapiSubmitRecord(timebill);
		nlapiLogExecution('DEBUG', 'Timebill ' + timebillid + ' successfully created', timebillid);
	}
	result.status = "success";
	result.timebill_id = timebillid;
	return result;
}

function ProjectsFor(data_in) {
	var search_id = 6546;
	return nlapiSearchRecord(null, search_id, null, null);
}

function validateTimeBills(data_in) {
	var timebills = data_in.timebill;
	var returnMessage = "";
	for (var timebillobject in timebills) {
		var timebill = timebills[timebillobject];
		var trandate = timebill.trandate;
		var customer = timebill.customer;
		var casetaskevent = timebill.casetaskevent;
		var hours = timebill.hours;
		var memo = timebill.memo;
		if (isNaN(nlapiStringToDate(trandate))) {
			returnMessage += "Invalid date: '" + trandate + "'\n";
		}
		if (customer == '') {
			returnMessage += "Customer entry cannot be blank.'\n";
		}
		if (hours == '') {
			returnMessage += "Hours cannot be blank.'\n";
		}
	}
	if (returnMessage)
	{
		nlapiLogExecution('DEBUG', 'Validation Error', returnMessage);
		return returnMessage;
	}
}
