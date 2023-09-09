const openModalSpinner = document.getElementById("buttonModalOpen");
    const closeModalSpinner = document.getElementById("buttonModalClose");

    const botonactualizar = document.getElementById("botonactualizar");

    const spinners = document.getElementsByName("opcionvista");

    for (spin of spinners) {
        spin.addEventListener('click', function(){
            //spinner.classList.add('spinner-visible');
            openModalSpinner.click();
        });
    }

    botonactualizar.addEventListener('click', function(){
        openModalSpinner.click();
    });