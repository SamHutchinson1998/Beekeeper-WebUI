const list = document.getElementById('list')

for (let i = 0; i < 50; i++) {
  const listItem = document.createElement('li')
  listItem.innerHTML = `list-item ${i}`
  list.appendChild(listItem)
}