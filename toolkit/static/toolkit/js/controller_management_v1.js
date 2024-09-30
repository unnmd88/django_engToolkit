'use strict';

/*------------------------------------------------------------------------
|                            Старт страницы                              |
------------------------------------------------------------------------*/

$(document).ready(function(){
    $(`#table_1`).show();

    $('.immutable_data_snmp').click(function() {
        let num_host;
        num_host = $(this).attr('id').split('_')[1];
        $(`#datahost_${num_host}`).text('--');
    });

    // $('.receive_data').click(function() {
    //     let num_host;
    //     console.log($(this).attr('id'));
    //     num_host = $(this).attr('id').split('_')[1];
    //     $(`#datahost_${num_host}`).text('--');
    // });

    // sendReqGetData();
    sendReqGetDataAxios();
    get_name_configs();

    $(`#table_1`).show();
});


/*------------------------------------------------------------------------
|                           Контент различных тегов                      |
------------------------------------------------------------------------*/



/*------------------------------------------------------------------------
|                                Константы                               |
------------------------------------------------------------------------*/

const CONTROLLERS = ['Swarco', 'Поток (S)', 'Поток (P)', 'Peek']
const TYPE_COMMAND = ['']


// --------------GET REQUEST SNMP------------------
// Отслеживаем нажатие чекбокса, который отвечает за постоянный запрос данных с дк по snmp у хоста 1

// Создаем функции на изменения чекбокс внутри каждого хоста
// for (let i=1; i < 11; i++) {
//     console.log(`Это i: ${i}`)
//     $(`#getdatahost_${i}`).change(function() {
//         console.log(intervalID)
    
//         console.log(`num_host = ${i}`)
    
//         if (chkbx[i-1].checked && !intervalID[i]){
//             let id_getData = setInterval(getData, 4000, i);
//             intervalID[i] = id_getData;
    
//         console.log('if');
    
//         }
//         else{
//             clearInterval(intervalID[i])
//             intervalID[i] = false;
//         console.log('else');
//         document.getElementById(`datahost_${i}`).textContent="--";
    
//         }
//         console.log(intervalID)
    
//         }
    
//     )
// }


// Клик на #display_hosts_snmp -> Отображение количества хостов

/*------------------------------------------------------------------------
|                            Обработчики событий                         |
------------------------------------------------------------------------*/

// Обработчик нажатие кнопку "Отобразить"(для хостов)
$("#display_hosts_snmp").click( function() {
    show_hide_hosts_snmp();
    } 
)

// Обработчик нажатие на чекбокс "Отметить/снять "Получать данные с ДК" для всех хостов"
$('#get_data_for_all_hosts').click(function(){
    select_deselect_hosts_snmp($(this).is(':checked'));
});

// Обработчик нажатие на чекбокс "Получать данные с дк"
$('.receive_data').click( function () {
    let num_host = $(this).attr('id').split('_')[1];
    if (!$(this).is(':checked')){
        $(`#datahost_${num_host}`).text('----');
    }
});

// Обработчик изменения протокола
$(`select[name=select_protocols]`).change( function () {
    let num_host = $(this).attr('id').split('_')[1];
    let protocol = $(`#protocol_${num_host} option:selected`).text();
    make_commands(num_host, protocol);
});


 
/*------------------------------------------------------------------------
|                     Функции для обработчиков событий                   |
------------------------------------------------------------------------*/

// Функция отображения количества хостов
function show_hide_hosts_snmp (option='standart') {
    console.log('ssssss')




    const select_visible_hosts = document.querySelector('#visible_hosts');
    const num_hosts_to_view = select_visible_hosts.value;
    console.log(`num_hosts_to_view -> ${num_hosts_to_view}`);

    if (option === 'load_from_db') {
        for(let i = 1; i <= +$('#visible_hosts option:last').val(); i++) {
            if (i <= num_hosts_to_view) {
                $(`#table_${i}`).show();
            }
            else {
                $(`#table_${i}`).hide();
            }
            
        }
        return;
    }












    if ($('#get_data_for_all_hosts').is(':checked')) {

        for (let i = 1; i <= +$('#visible_hosts option:last').val(); i++) {

            if(i <= num_hosts_to_view) {
                $(`#table_${i}`).show();
                $(`#getdatahost_${i}`).prop('checked', true);
            }
            else {
                $(`#table_${i}`).hide();
                $(`#getdatahost_${i}`).prop('checked', false);
            }
        }            
    }
    else {
        for (let i = 1; i <= +$('#visible_hosts option:last').val(); i++) {

            if(i <= num_hosts_to_view) {
                $(`#table_${i}`).show();
            }
            else {
                $(`#getdatahost_${i}`).prop('checked', false);
                $(`#table_${i}`).hide();
                
            }
        }            
    }
}

// Функция снять/выбрать все хосты
function select_deselect_hosts_snmp (condition) {
    console.log(condition);

    if (!condition) {
        $('.receive_data').prop('checked', false);
        $('.label_datahost').text('----');
    }
    else {
        $('.receive_data').each(function () {
        console.log('scsdc');
        if ($(this).is(":visible")) {
            $(this).prop('checked', true);
        }
        else {
            let num_host = $(this).attr('id').split('_')[1];
            $(this).prop('checked', false);
            $(`#datahost_${num_host}`).text('----');
        }
    });
    }
}

function make_commands(num_host, protocol) {
    const protocols = ['Поток (P)', 'Поток (S)', 'Swarco', 'Peek'];
    let commands_content;
    if (protocol === protocols[0]) {
        commands_content = ['Фаза SNMP', 'ОС SNMP', 'ЖМ SNMP', 'Рестарт программы'];
    }
    else if (protocol === protocols[1]) {
        commands_content = ['Фаза SNMP', 'ОС SNMP', 'ЖМ SNMP', 'КК SNMP', 'Рестарт программы'];
    }
    else if (protocol === protocols[2]) {
        commands_content = ['Фаза SNMP', 'Фаза MAN', 'Терминальная команда', 'ОС SNMP', 'ЖМ SNMP', 'КК SNMP', 'Перезагрузка ДК'];
    }
    else if (protocol === protocols[3]) {
       commands_content = ['Фаза SNMP', 'Фаза MAN', 'ОС MAN', 'ЖМ MAN', 'КК CP_RED','Вводы', 'Параметры программы', 'Перезагрузка ДК'];
    }
    else {
        $(`#setCommand_${num_host} option`).remove();
        $(`#setCommand_${num_host}`).append(`<option value="1"> Выберите протокол </option>`);
        return;
    }

    $(`#setCommand_${num_host} option`).remove();

    $.each(commands_content,  function(tag_val, val) {
        $(`#setCommand_${num_host}`).append(`<option value="${++tag_val}">${val}</option>`);
    });

}

/*------------------------------------------------------------------------
|                 Сохранение и загрузка конфигурации в БД                 |
------------------------------------------------------------------------*/

// const csrftoken = getCookie('csrftoken');
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = jQuery.trim(cookies[i]);
//             if (cookie.startsWith(name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break; // Выходим, как только найдём нужное cookie
//             }
//         }
//     }
//     return cookieValue;
// }


// Сохранение и загрузка конфигурации в БД
$("#send_data_to_db").click( function() {
    if (!confirm('Хотите добавить текущие настройки хостов в базу данных ?')) {
        return false;
    }
    send_data_to_db_ax();
    } 
)

$("#get_data_from_db").click( function() {
    alert('sdfsfdsb');
    get_data_from_db_ax();
    } 
)

// Обработчик нажатия на выпадающий список "загрзить конфигурацию из дб"
// $(`select[name=conf_from_db]`).click( function () {
//     get_name_configs();
// });

async function get_name_configs() {
    // let csrfToken = $("input[name=csrfmiddlewaretoken]").val();
    try {
        const response = await axios.get(`/api/v1/get-names-configuration-controller-management-ax/`);

        console.log('response.data');
        console.log(response.data);

        $(`#configuration_from_db option`).remove();
        for (const [num_host, write_data] of Object.entries(response.data)) {
            $(`#configuration_from_db`).append(`<option value="${num_host}">${write_data}</option>`);
          }

      } catch (error) {
        if (error.response) { // get response with a status code not in range 2xx
          console.log(error.response.data);
          console.log(error.response.status);
          console.log(error.response.headers);
        } else if (error.request) { // no response
          console.log(error.request);
        } else { // Something wrong in setting up the request
          console.log('Error', error.message);
        }
        console.log(error.config);
      }
    
 }

// Функция получает данные настроек хостов из БД и записывает их в соответствующие теги
async function get_data_from_db_ax() {

    let name = $(`#configuration_from_db option:selected`).text();
    try {
        const response = await axios.get(            
            `api/v1/get-configuration-controller-management-ax/`,
            {
                params: {
                    name_configuration: name,
                },
            },

        );
        console.log('response.data');
        console.log(response.data);
        // get_name_configs();
        
        let resp_data = response.data;
        console.log('visible_hosts.data');
        console.log(resp_data);
        console.log(resp_data['num_visible_hosts']);
        console.log(resp_data['data']);

        write_data_from_db_to_all_hosts(resp_data['num_visible_hosts'], resp_data['data']);
        if (resp_data.result) {
            alert(`Конфигурация "${name}" загружена из БД`); 
        }
        else {
            alert(`Сбой при загрузке конфигурация "${name}" из БД`); 
        } 

        // let data_to_write = response.data;

        // for (const [num_host, write_data] of Object.entries(response.data)) {
        //     $(`#datahost_${num_host}`).text(write_data);
        //   }


      } catch (error) {
        if (error.response) { // get response with a status code not in range 2xx
          console.log(error.response.data);
          console.log(error.response.status);
          console.log(error.response.headers);
        } else if (error.request) { // no response
          console.log(error.request);
        } else { // Something wrong in setting up the request
          console.log('Error', error.message);
        }
        console.log(error.config);
      }
    
 }

 // Функция записывает данные в теги инфу из бд
 function write_data_from_db_to_all_hosts (visible_hosts, datahosts) {
    let splited_data;

    $.each(datahosts, function(cur_host, write_data) {
        splited_data = write_data.split(';');
        // console.log(splited_data);
        $(`#ip_${cur_host}`).val(splited_data[0]);
        $(`#scn_${cur_host}`).val(splited_data[1]);
        $(`#protocol_${cur_host} option:contains(${splited_data[2]})`).prop('selected', true);
        make_commands(cur_host, $(`#protocol_${cur_host} option:selected`).text());
        splited_data[3] === 'true' ? $(`#getdatahost_${cur_host}`).trigger('click') : $(`#getdatahost_${cur_host}`).prop('checked', false);
        $(`#setCommand_${cur_host} option:contains(${splited_data[4]})`).prop('selected', true);
        $(`#setval_${cur_host}`).val(splited_data[5]);
        splited_data[6] === 'true' ? $(`#hold_${cur_host}`).prop('checked', true) : $(`#hold_${cur_host}`).prop('checked', false); 

    });
    $(`#visible_hosts option[value=${visible_hosts}]`).prop('selected', true);
    show_hide_hosts_snmp('load_from_db');
 }

// Функция проверяет валидность введённого имени в тектовое поле name_configuration_datahosts
function check_valid_data_send_to_db (val_name) {
    if (val_name.replace(/ /g,'').length < 3) {
        return false;
    }        
    return true;
}

// Функция собирает данные всех хостов(для отправки в БД)
function collect_data_from_all_hosts () {
    let num_hosts = +$('#visible_hosts option:last').val();
    let data = {name: $(`#name_configuration_datahosts`).val(),
                num_visible_hosts: $(`#visible_hosts option:selected`).text(), 
               };
    for (let cur_host = 1; cur_host <= num_hosts; cur_host++) {
        data[cur_host] = `${$('#ip_' + cur_host).val()};` + 
                         `${$(`#scn_${cur_host}`).val()};` +                         
                         `${$(`#protocol_${cur_host} option:selected`).text()};` + 
                         `${$(`#getdatahost_${cur_host}`).is(":checked")};` + 
                         `${$(`#setCommand_${cur_host} option:selected`).text()};` +
                         `${$(`#setval_${cur_host}`).val()};` + 
                         `${$(`#hold_${cur_host}`).is(":checked")};`                         
                    }
    // console.log('dataaa')
    // console.log(data)
    return data;

}

// Асинхронный скрипт отправки данных конфигурации в БД
 async function send_data_to_db_ax () {

    const name_configuration = document.querySelector('#name_configuration_datahosts').value;

    if (!check_valid_data_send_to_db(name_configuration)) {
        alert('Название конфигурации должно быть более 3 символов');
        return false;
    }

    let select_vals = document.querySelectorAll('#configuration_from_db option');
    console.log('select_vals');
    console.log(select_vals);

    for (let element of select_vals) {
        if (element.text === name_configuration) {
            console.log(`Конфигурация с таким названием "${element.text}" уже есть`);
            return false;
        }
        
    }

    let csrfToken = $("input[name=csrfmiddlewaretoken]").val();
    try {
        const response = await axios.post(            
            `/api/v1/save-configuration-controller-management-ax/`,
            {
              data: collect_data_from_all_hosts(),
            },
            {  
              headers: {
              "X-CSRFToken": csrfToken, 
              "content-type": "application/json"
              }
            }
        );

        const res = response.data;
        console.log('res[result]');
        console.log(res['result']);
        if (res['result']) {
            alert('Конфигурация успешно сохранена');
            get_name_configs();
        }
        else {
            alert('Сбой при сохранении конфигурации');
        }  
        console.log('response.data');
        console.log(typeof(response.data));
        console.log(response.data);
        
        // let data_to_write = response.data;

        for (const [num_host, write_data] of Object.entries(response.data)) {
            $(`#datahost_${num_host}`).text(write_data);
          }


      } catch (error) {
        if (error.response) { // get response with a status code not in range 2xx
          console.log(error.response.data);
          console.log(error.response.status);
          console.log(error.response.headers);
        } else if (error.request) { // no response
          console.log(error.request);
        } else { // Something wrong in setting up the request
          console.log('Error', error.message);
        }
        console.log(error.config);
      }
    
 }

 /*------------------------------------------------------------------------
|                         GET CURRENT STATE                               |
--------------------------------------------------------------------------*/


function collect_data_from_hosts (){
    let num_visible_hosts = $(`#visible_hosts`).val();
    let data = {};
    let num_checked_checkbox = $('.receive_data:checked').length;
    if (num_checked_checkbox > 0) {
        for(let num_host = 1, all_hosts = 0; num_host <= num_visible_hosts; num_host++) {   
            if ($(`#getdatahost_${num_host}`).is(':checked')){
                data[num_host] = `${$('#ip_' + num_host).val()};${$(`#protocol_${num_host} option:selected`).text()};${$(`#scn_${num_host}`).val()}`;
                data.num_hosts_in_request = ++all_hosts;
            }           
        }
    }
        //  console.log(data);
    return data;
    }




async function sendReqGetDataAxios() {
    console.log('sendReqGetDataAxios');
    

    let num_checked_checkbox = $('.receive_data:checked').length;
    if (num_checked_checkbox > 0) {
        console.log('if (num_checked_checkbox > 0)');
        try {
            const response = await axios.get(
                `get-data-snmp-ax/1/`,
                {
                  params: collect_data_from_hosts()
                }
            );
            console.log('response.data');
            console.log(response.data);
            // let data_to_write = response.data;

            for (const [num_host, write_data] of Object.entries(response.data)) {
                $(`#datahost_${num_host}`).text(write_data);
              }
   
    
          } catch (error) {
            if (error.response) { // get response with a status code not in range 2xx
              console.log(error.response.data);
              console.log(error.response.status);
              console.log(error.response.headers);
            } else if (error.request) { // no response
              console.log(error.request);
            } else { // Something wrong in setting up the request
              console.log('Error', error.message);
            }
            console.log(error.config);
          }

          let val_interval = +$('#polling_get_interval').val();       
          if(Number.isInteger(val_interval)) {
              val_interval = +val_interval;
              if (val_interval === 0) {
                  setTimeout(sendReqGetDataAxios, 1000);
              }
              else {
                  val_interval = val_interval * 1000;
                  setTimeout(sendReqGetDataAxios, val_interval);
              }        
          }

          else {
              setTimeout(sendReqGetDataAxios, 1000);
          }



    }

    else {
        let val_interval = +$('#polling_get_interval').val();
        if(Number.isInteger(val_interval)) {
            val_interval = +val_interval;
            if (val_interval === 0) {
                setTimeout(sendReqGetDataAxios, 1000);
            }
            else {
                val_interval = val_interval * 1000;
                setTimeout(sendReqGetDataAxios, val_interval);
            }        
        }
        else {
            setTimeout(sendReqGetDataAxios, 1000);
        }   
    } 

}

 /*------------------------------------------------------------------------
|                               SET REQUEST                                |
--------------------------------------------------------------------------*/


let set_timers = {};
let set_timerID;
let test_timers = [];

$(".set_request").click(function (){
    console.log(`set_timers = ${set_timers}`);
    console.log('Tetss SET');
    let num_host = $(this).attr('id').split('_')[1];

    console.log(`test_timers начало`);
    console.log(test_timers);

    if (set_timers.hasOwnProperty(num_host)) {
        console.log(`set_timers из if первая строчка = ${set_timers}`);
        console.log(set_timers);
        console.log(test_timers);
        clearInterval(set_timers[num_host]);
        $(`#setTimerVal_${num_host}`).text(0);
        set_timers[num_host] = null;

        set_timerID = setInterval(write_setTimerVal, 1000, num_host);
        test_timers.push(set_timerID);
        set_timers[num_host] = set_timerID;
        console.log(`set_timers из if последняя строчка = ${set_timers}`);
        console.log(set_timers);
        console.log(test_timers);
    }

    else {
        console.log(`set_timers из else первая строчка`);
        console.log(set_timers);
        console.log(test_timers);
        
        set_timerID = setInterval(write_setTimerVal, 1000, num_host);
        set_timers[num_host] = set_timerID;
        test_timers.push(set_timerID);
        console.log(`set_timers из else послдняя строчка`);
        console.log(set_timers);
        console.log(test_timers);
    }
}
);

$(".hold_request").click(function () {
    let num_host = $(this).attr('id').split('_')[1];
    let tags = [`#ip_${num_host}`, `#scn_${num_host}`, `#protocol_${num_host}`,
                `#setCommand_${num_host}`, `#setval_${num_host}`, `#SetToHost_${num_host}`]


    if (check_valid_data_hold_request(num_host) && $(`#hold_${num_host}`).is(':checked')) {
        tags.forEach((element) => document.querySelector(element).disabled = true);
    }
    else {
        tags.forEach((element) => document.querySelector(element).disabled = false);
    }
}
);

// Функция записывает значение, какое количество секунд назад была отправлена команда set_request,
// а также вызывает функцию повторной отправки set_request(удержание)
async function write_setTimerVal (num_host) {

    let curr_val = +$(`#setTimerVal_${num_host}`).text();
    $(`#setTimerVal_${num_host}`).text(++curr_val);

    let dataIsValid = check_valid_data_hold_request(num_host);
    let checkboxIsChecked = $(`#hold_${num_host}`).is(':checked');
    

    if (curr_val % 20 === 0 && dataIsValid && checkboxIsChecked) {
        console.log('axios');
        set_request_axios (num_host);
}
}

function sendRequstCommon (num_host) {
    $.ajax({

        type: "POST",
        url: `set_snmp_ajax/${num_host}/`,
        data: {values: 'ТЕСТ ПОСТ ЗАПРОСА',
               csrfmiddlewaretoken:$("input[name=csrfmiddlewaretoken]").val(),
        },
    
        dataType: 'text',
        cache: false,
        success: function (data) {
        console.log(data)
        if (data == 'yes'){
        console.log(data);
            }
        else if (data == 'no'){
                }
            }
        }
    );
 }

// Отправка set request по id кнопки отправить
 $('.set_request').click(function() {
    let num_host = $(this).attr('id').split('_')[1];;
    // console.log($(this).attr('id'));

    console.log(num_host);
    let data_request = {};
    // data[num_host] = (`${$('#ip_' + num_host).val()};
    //                    ${$(`#protocol_${num_host} option:selected`).text()};
    //                    ${$(`#scn_${num_host}`).val()};
    //                    ${$(`#setCommand_${num_host} option:selected`).text()}=${$('#setval_' + num_host).val()}                       
    //                    `);
    data_request[num_host] = `${$('#ip_' + num_host).val()};` + 
                             `${$(`#protocol_${num_host} option:selected`).text()};` + 
                             `${$(`#scn_${num_host}`).val()};` + 
                             `${$(`#setCommand_${num_host} option:selected`).text()};` +
                             `${$('#setval_' + num_host).val()}`

    $(`#recieve_data_from_terminal_${num_host}`).text('Команда отправлена');

    console.log(data_request);

    $.ajax({
        type: "POST",
        url: `set-snmp-ajax/${num_host}/`,
        data: data_request,
        headers: {
            'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val(),
        },
        dataType: 'text',
        cache: false,
        success: function (data) {
        let postStringify = JSON.parse(data);

        $.each(postStringify, function(num_host, write_data) {
            let content = write_data.replace('\n', "<br>");
            console.log(content);
            $(`#recieve_data_from_terminal_${num_host}`).html(content);
        });

        console.log(data)
        if (data == 'yes'){
        console.log(data);
            }
        else if (data == 'no'){
                }
            }
        }
    );


});

function check_valid_data_hold_request (num_host) {

    console.log('зашел в function check_valid_data_hold_request');

    let allowed_data_to_hold = {};       
    allowed_data_to_hold[CONTROLLERS[0]] = ['Фаза SNMP'];
    allowed_data_to_hold[CONTROLLERS[1]] = ['Фаза SNMP', 'ОС SNMP', 'ЖМ SNMP', 'КК SNMP'];
    allowed_data_to_hold[CONTROLLERS[2]] = ['Фаза SNMP', 'ОС SNMP', 'ЖМ SNMP'];
    allowed_data_to_hold[CONTROLLERS[3]] = ['Фаза SNMP', 'ОС SNMP', 'ЖМ SNMP', 'КК SNMP'];
    allowed_data_to_hold[CONTROLLERS[3]] = ['Фаза SNMP'];

    let controller_type = `${$(`#protocol_${num_host} option:selected`).text()}`;
    let type_command = `${$(`#setCommand_${num_host} option:selected`).text()}`;

    const commands_content = ['Фаза SNMP', 'ОС SNMP', 'ЖМ SNMP', 'КК SNMP'];

    
    if (!CONTROLLERS.includes(controller_type)){
        console.log('1')
        return false;
    };

    if (type_command === commands_content[0]) {
        console.log('2')
        return true;
    }
    else if (controller_type === CONTROLLERS[1] && allowed_data_to_hold[CONTROLLERS[1]].includes(type_command)) {
        console.log('3')
        return true;
    }
    else if (controller_type === CONTROLLERS[2] && allowed_data_to_hold[CONTROLLERS[2]].includes(type_command)) {
        console.log('4')
        return true;
    }
    else {
        console.log('5')
        return false;
    }
};


// Отправка повторного запроса(удержание) с помощью библиотеки axios
function set_request_axios (num_host) {

    let data_request = {};
        data_request[num_host] = `${$('#ip_' + num_host).val()};` + 
                                 `${$(`#protocol_${num_host} option:selected`).text()};` + 
                                 `${$(`#scn_${num_host}`).val()};` + 
                                 `${$(`#setCommand_${num_host} option:selected`).text()};` +
                                 `${$('#setval_' + num_host).val()}`

        axios({
            method: 'post',
            url: `set-data-snmp-ax/${num_host}/`,
            data: data_request,
            headers: {
              "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(), 
              "content-type": "application/json"
            }
          }).then(function (response) {
            console.log(`response`);
            // console.log(response);
            console.log(response.data);

          }).catch(function (error) {
            console.log(error)
          });
    }



/*
------------------------------------------------
*****               ARCHIVE                *****
------------------------------------------------

// Функция получния данных о режиме ДК ajax(требует запуска при загрузке страницы)

// function sendReqGetData () {
//     let num_checked_checkbox = $('.receive_data:checked').length;
//     if (num_checked_checkbox > 0) {
       
          
//         $.ajax({
//         type: "GET",
//         url: `get-data-snmp/1/`,
//         data: collect_data_from_hosts(),
    
//         dataType: 'text',
//         cache: false,
//         success: function (data) {
//         // console.log(data)
//         let postStringify = JSON.parse(data);
//         console.log(postStringify);
    
//         $.each(postStringify, function(num_host, write_data) {
//             $(`#datahost_${num_host}`).text(write_data);
//         });
    
//         let val_interval = +$('#polling_get_interval').val();       
//         if(Number.isInteger(val_interval)) {
//             val_interval = +val_interval;
//             if (val_interval === 0) {
//                 setTimeout(sendReqGetData, 1000);
//             }
//             else {
//                 val_interval = val_interval * 1000;
//                 setTimeout(sendReqGetData, val_interval);
//             }        
//         }
//         else {
//             setTimeout(sendReqGetData, 1000);
//         }    
//         // console.log(val_interval)
//         // console.log('recursion')
//         }
//         });
//     }

//     else {
//         let val_interval = +$('#polling_get_interval').val();
//         if(Number.isInteger(val_interval)) {
//             val_interval = +val_interval;
//             if (val_interval === 0) {
//                 setTimeout(sendReqGetData, 1000);
//             }
//             else {
//                 val_interval = val_interval * 1000;
//                 setTimeout(sendReqGetData, val_interval);
//             }        
//         }
//         else {
//             setTimeout(sendReqGetData, 1000);
//         }   
//     } 
// }



// Функция загрузки конфигурации из бд
function get_data_from_db () {
    $.ajax({
        // $(`#protocol_${num_host} option:selected`).text()
        type: "POST",
        url: `get-configuration-controller-management/`,
        data: {
            name_configuration: $(`#id_configuration_from_db option:selected`).text()
        },
        headers: {
            'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val(),
        },
    
        dataType: 'text',
        cache: false,
        success: function (data) {
        // console.log(data)
        
        let postStringify = JSON.parse(data);
        // console.log(postStringify);

        let visible_hosts, datahosts;
        visible_hosts = postStringify.num_visible_hosts;
        datahosts = postStringify.data.replace(/'/ig, '"');
        datahosts = JSON.parse(datahosts);
        console.log(datahosts);

        write_data_from_db_to_all_hosts(visible_hosts, datahosts);
        alert('Конфигурация загружена из БД');   

        }
    });
    
 }



// Скрипт отправки данных конфигурации в БД
 function send_data_to_db () {
    if (!check_valid_data_send_to_db()) {
        alert('Название конфигурации должно быть более 3 символов');
        return false;
    }

    $.ajax({        
        type: "POST",
        url: `save-configuration-controller-management/`,
        data: collect_data_from_all_hosts(),
        headers: {
            'X-CSRFToken': $("input[name=csrfmiddlewaretoken]").val(),
        },
        dataType: 'text',
        cache: false,
        success: function (data) {
        let result = JSON.parse(data);
        if (result.result) {
            alert('Конфигурация успешно сохранена');
        }    
        // console.log(result);
        // console.log(result.result);
            }
        }
    );
 }




*/