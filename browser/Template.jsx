import { useEffect } from 'react';

function Template() {
    useEffect(() => {
        // 確保網頁中只會插入一次這個樣式標籤，避免重複渲染產生多個 style
        const styleId = 'dynamic-flex-style';
        if (!document.getElementById(styleId)) {
            const cssRules = `
                .flex {
                    display: flex;
                    gap: 3px;
                }
            `;
            const styleElement = document.createElement('style');
            styleElement.id = styleId;
            styleElement.type = 'text/css';
            
            if (styleElement.styleSheet) {
                styleElement.styleSheet.cssText = cssRules;
            } else {
                styleElement.appendChild(document.createTextNode(cssRules));
            }
            document.head.appendChild(styleElement);
        }
    }, []);

    return (
        <>
            <h1>Template</h1>
            <h2>Template</h2>
            <h3>Template</h3>
            <h4>Template</h4>
            <h5>Template</h5>
            <h6>Template</h6>
            <hr />
            <datalist id="input-list">
                <option value="aaa" />
                <option value="bbb" />
                <option value="ccc" />
                <option value="ddd" />
            </datalist>
            
            
            <div className="flex">
                <span>hello許功蓋</span>
                <input type="text" placeholder="text許功蓋" list="input-list" />
                <input type="number" placeholder="number" />
                <input type="search" placeholder="search許功蓋" list="input-list" />
            </div>

            <div className="flex">
                <button>Hello許功蓋</button>
                <input type="submit" placeholder="submit" />
                <input type="range" />
                <progress value="0.3"></progress>
            </div>

            <div className="flex">
                <span>hello</span>
                <label><input type="checkbox" placeholder="checkbox" />Hello許功蓋</label>
                <label><input type="radio" placeholder="radio" name="v" value="1" />Hello許功蓋</label>
                <label><input type="radio" placeholder="radio" name="v" value="2" />Hello許功蓋</label>
                <input type="file" placeholder="file" />
                <input type="reset" placeholder="reset" />
                <input type="button" placeholder="button" value="hello" />
                <meter min="0" low="30" high="60" optimum="70" max="100" value="20"></meter>
            </div>

            <div className="flex">
                <input type="date" placeholder="date" />
                <input type="datetime" placeholder="date" />
                <input type="datetime-local" placeholder="date" />
            </div>

            <div className="flex">
                <input type="month" placeholder="date" />
                <input type="week" placeholder="date" />
                <input type="time" placeholder="date" />
            </div>

            <div className="flex">
                <select>
                    <optgroup label="Gruop1">
                        <option>AAA</option>
                        <option>BBB</option>
                        <option>CCC</option>
                    </optgroup>
                    <optgroup label="Gruop2">
                        <option>DDD</option>
                        <option>EEE</option>
                        <option>FFF</option>
                    </optgroup>
                </select>

                <code>
                    print("hello")
                </code>
            </div>
        </>
    );
}

export default Template;