var url = new URL(document.URL);
var items = document.getElementsByClassName("sort-item");

// Setar para cada item a URL
for (i = 0; i < items.length; i++) {
    url.searchParams.set("ordem", items[i].name);
    //editar item para receber p href
    items[i].href = url.href;
}



console.log(url);