$(document).ready(main);

console.log("Script loaded");

function log() {
    console.log("Button clicked");
}

function populateInfectionsTable() {
    // * Clearing the table
    $('#inf-table').empty();

    var infections = {
        'influenza': 'Influenza (flu)',
        'pneumonia': 'Pneumonia',
        'ecoli': 'E. Coli',
        'covid': 'COVID-19',
        'malaria': 'Malaria',
        'cholera': 'Cholera',
        'cold': 'Common Cold',
        'tb': 'Tuberculosis (TB)',
    }

    // * Fixing the table to 2 columns
    var n_infections = Object.keys(infections).length;
    var cols = 2;
    var rows = Math.ceil(n_infections/cols);
    var inf_index = 0;

    // * Populating the table
    for(var r=0; r<rows; r++) {
        let row_block = '<tr>';
        for(var c=0; c<2 & inf_index<n_infections; c++, inf_index++) {
            let cell = '<td>';  
            let [key, value] = Object.entries(infections)[inf_index];
            let checkbox = '<input type="checkbox" name="infHistory" value="'+key+'"> '+value+'<br>';
            cell += checkbox;
            cell += '</td>';
            row_block += cell;
        }
        row_block += '</tr>';
        $('#inf-table').append(row_block);
    }
}

function main() {
    $('#dummy-btn').click(function() {
        console.log("Button clicked 1");
    });

    $('#modal-confirm').click(function() {
        console.log("Submitting form.");
        // check if required fields are filled
        $('#exampleModal').on('hidden.bs.modal', function (e) {
            console.log("Modal closed");
            $('#screen-submit').click();
        });
    });

    // populateInfectionsTable();
}