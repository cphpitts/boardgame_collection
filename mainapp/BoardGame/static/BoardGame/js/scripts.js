function showModal() {
    $('#gamePickerModal').modal('show')
    chooseGame()


}

function chooseGame() {
    gameContainers = document.querySelectorAll('.game_container .game_text');
    gameNum = gameContainers.length;
    pickedNum = Math.floor(Math.random() * gameNum);
    pickedGame = gameContainers[pickedNum].innerText;
    modalBody = document.querySelector('#gamePickerModal .modal-body');
    modalBody.innerHTML = "You should play " + pickedGame;
}
