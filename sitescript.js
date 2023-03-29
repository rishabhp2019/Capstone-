const username = document.getElementById('username')
const password = document.getElementById('password')
const form = document.getElementById('Form')
const errorElement = document.getElementById('error')

form.addEventListener('submit', (e) => {
    let messages = []
    if(username.value === '' || username.value == null){
        messages.push('usename is required')
    }
    if (password.value.length <= 6){
        messages.push('Password must be longer than 6 characters')
    }
    if (password.value.length >= 20){
        messages.push('Password is too long')
    }
    if(password.value == 'password'){
        messages.push('Password cannot be password')
    }
    if (messages.length > 0){
        e.preventDefault()
        errorElement.innterText = messages.join(' , ')
    }
})
