$(document).ready(main);

console.log("Script loaded");

function buttonclick() {
    console.log("Button clicked");
}

function populateInfectionsTable() {
    // * Clearing the table
    $('#inf-table').empty();

    var infectionsArray = [
        ['influenza', 'Influenza (flu)'],
        ['pneumonia', 'Pneumonia'],
        ['ecoli', 'E. Coli'],
        ['covid', 'COVID-19'],
        ['malaria', 'Malaria'],
        ['cholera', 'Cholera'],
        ['cold', 'Common Cold'],
        ['tb', 'Tuberculosis (TB)'],
    ]

    // const validateInfection = (infection) => {
    //     if (!Array.isArray(infection) | infection.length != 2) {
    //         return false;
    //     }
    //     if (!infection.every((value) => typeof value === 'string')) {
    //         return false;
    //     }
    //     return true;
    //     // return !(!Array.isArray(infection) || infection.length != 2 || !infection.every((value) => typeof value === 'string'))
    //     // return Array.isArray(infection) && infection.length == 2 && infection.every((value) => typeof value === 'string')
    // }

    // * Validating the array
    // valid = infectionsArray.every(validateInfection);
    valid = infectionsArray.every((infection) => Array.isArray(infection) && infection.length == 2 && infection.every((value) => typeof value === 'string'))
    if (!valid) {
        throw new Error("Invalid infectionsArray");
    }

    var infectionsObj = Object.fromEntries(infectionsArray);

    var infectionsArrayObjs = infectionsArray.map(([value, label]) => ({value, label}));

    var infectionsMap = new Map(infectionsArray);
    // infectionsKeysByIndex = [...infectionsMap.keys()]; // * Array of keys [...<map iterator>]; Takes O(n) space => not good for large maps, better to use iterator or an array.
    
    
    // * Fixing the table to 2 columns
    var n_infections = infectionsArray.length;
    // var n_infections = Object.keys(infectionsObj).length;
    // var n_infections = infectionsMap.size;
    var cols = 2;
    var rows = Math.ceil(n_infections/cols);
    var inf_index = 0;
    
    // * Populating the table
    // var infectionsMapIterator = infectionsMap.entries(); // * Map iterator
    for (var r = 0; r < rows; r++) { 
        let row_block = '<tr>';
        for (var c = 0; c < 2 & inf_index < n_infections; c++, inf_index++) {
            let cell = '<td>';  
            
            // * If using Object
            // let [value, label] = Object.entries(infectionsObj)[inf_index];
            
            // * If using Map and defining the keys array
            // let value = infectionsKeysByIndex[inf_index];

            // * If using Map with iterator
            // let nextItem = infectionsMapIterator.next();
            // if (nextItem.done) break;
            // let [value, label] = nextItem.label;

            // * If using Array
            let [value, label] = infectionsArray[inf_index];

            // * If using Array of Objects
            // let {value, label} = infectionsArrayObjs[inf_index];

            let checkbox = `<input type="checkbox" name="infHistory" value="${value}"> ${label}<br>`
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