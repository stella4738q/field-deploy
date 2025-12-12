export default function (getPermissionMenuItem) {
    const vm = this;
    var result = {
        flatRule: [],
        flatApi: [],
        flatPage: [],
    };

    // result.flatRule.push( { 
    //     name:"一般",
    //     menu : getPermissionMenuItem.filter( x=> {
    //         return x.children.length == 0
    //     })
    // })

    getPermissionMenuItem.filter(item => {
        return item.children.length > 0
    }).forEach(item => {
        var menu = [];
        item.children.forEach(subItem => {
            if (subItem.children.length == 0) {
                menu.push(subItem)
            } else {
                subItem.children.forEach(subSubItem => {
                    subSubItem.name = subItem.name + "-" + subSubItem.name;
                    menu.push(subSubItem);
                })
            }
        });

        result.flatRule.push({
            name: item.name,
            menu: menu
        });
    });

    result.flatRule.forEach(x => {
        x.menu.forEach(xx => {
            result.flatApi.push(...xx.api_list);
        });
        result.flatPage.push(...x.menu.filter(x => {
            return x.enable == true
        }).map(x => {
            return x.code
        }));
    });

    return result;
}