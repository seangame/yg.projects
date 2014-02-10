// borrowed from http://blog.prolecto.com/2011/12/18/netsuite-restlet-sample-program-exploits-new-power/

function CreateTimebills(data_in) {
	var output = '';
	//nlapiLogExecution('DEBUG','createRecord',(typeof data_in.timebill));
	var msg = validateTimeBills(data_in);
	if (msg) {
		var err = new Object();
		err.status = "failed";
		err.message= msg;
		return err;
	}
	var timebills = data_in.timebill;
	for (var timebillobject in timebills) {
		var timebill = timebills[timebillobject];
		var trandate = timebill.trandate;
		var customer = timebill.customer;
		var casetaskevent = timebill.casetaskevent;
		var hours = timebill.hours;
		var memo = timebill.memo;
		var timebill = nlapiCreateRecord( 'timebill' );
		timebill.setFieldValue( 'trandate', trandate);
		timebill.setFieldText( 'customer', customer);
		timebill.setFieldText( 'casetaskevent', casetaskevent);
		timebill.setFieldValue( 'memo', memo);
		timebill.setFieldValue( 'hours', hours);
		var timebillid = nlapiSubmitRecord( timebill );
		nlapiLogExecution('DEBUG','Timebill ' + timebillid + ' successfully created',timebillid);
	}
	return;
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
		if (casetaskevent == '') {
			returnMessage += "Case Task Event entry cannot be blank.'\n";
		}
		if (hours == '') {
			returnMessage += "Hours cannot be blank.'\n";
		}
		if (memo == '') {
			returnMessage += "Memo cannot be blank.'\n";
		}
	}
	if (returnMessage)
	{
		nlapiLogExecution('DEBUG','Validation Error',returnMessage);
		return returnMessage;
	}
}
