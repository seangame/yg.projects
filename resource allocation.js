function CreateAllocation(allocation) {
    // allocation should be an object with the required properties:
    // amount, resource_id, type, unit, and project.
    var result = new Object();

    var record = nlapiCreateRecord('resourceallocation');
    record.setFieldValue('allocationamount', allocation.amount);
    record.setFieldValue('allocationresource', allocation.resource_id);
    record.setFieldValue('allocationtype', allocation.type);
    record.setFieldValue('allocationunit', allocation.unit);
    record.setFieldValue('project', allocation.project_id);
    if(allocation.start_date) {
        var start_date = new Date(allocation.start_date);
        var ns_start_date = nlapiDateToString(start_date, "date");
        record.setFieldValue('startdate', ns_start_date);
    }
    if(allocation.end_date) {
        var end_date = new Date(allocation.end_date);
        var ns_end_date = nlapiDateToString(end_date, "date");
        record.setFieldValue('enddate', ns_end_date);
    }
    if(allocation.notes) {
        record.setFieldValue('notes', allocation.notes);
    }
    var recId = nlapiSubmitRecord(record);
    nlapiLogExecution('DEBUG', 'ResourceAllocation ' + recId + ' successfully created', recId);

    result.status = 'success';
    result.id = recId;
    return result;
}
