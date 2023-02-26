
// Listen to changes in specialties drop down 
var specialty = document.querySelector("#id_specialties");
specialty.addEventListener("change", fetchSpecialists)


/**
 * Replace employee select options with those fetched by fetchSpecialists func.
 * 
 * @param data - text (html generated in main/includes/specialists.html) 
 * representation of available options
 */
function replaceEmployeeSelectOptions(data) {
    var empSelect = document.getElementById("id_employee");
    empSelect.innerHTML = data;
}

/**
 * Fetch employees assigned to selected specialty groups. Pass them as text
 * (html) to replaceEmployeeSelectOptions.
 * @param e - change event on specialties drop down.
 */
async function fetchSpecialists(e) {
    var url = document.querySelector("#schedule-form").getAttribute("specialties-url")
    var text = e.target.options[e.target.selectedIndex].text;
    url = url + "?" + "specialty=" + text
    response = await fetch(url, {
        method: "GET",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    });

    var data = await response.text();
    replaceEmployeeSelectOptions(data);
}

