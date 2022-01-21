// script async="" src="/Ss13U803/init.js"></script>
// attempt to delete js scripts from loading

const remove_async_elements = () => {
    let head = document.getElementsByTagName('head')[0];
    let async_tags = head.querySelectorAll('head > script[async_tags]');
    for (i = 0; i < async_tags.length; i++) {
        head.removeChild(async_tags[i]);
    }
}

