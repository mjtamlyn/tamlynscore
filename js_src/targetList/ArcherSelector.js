import React, { useState, useEffect, useRef } from 'react';

import useMousetrap from 'react-hook-mousetrap';

import ArcherPills from '../utils/ArcherPills';
import textMatcher from '../utils/textMatcher';


const ArcherSelector = ({ archers, onSelect, close, emptyLabel="Select…" }) => {
    const ref = useRef(null);
    const closeHandler = (e) => {
        if (ref && !ref.current.closest('.archer-block').contains(e.target)) {
            close();
        }
    };
    useEffect(() => {
        document.body.addEventListener('click', closeHandler);
        return () => document.body.removeEventListener('click', closeHandler);
    }, []);
    useMousetrap('esc', close);

    const [search, setSearch] = useState('');
    const [selected, setSelected] = useState(null);
    const selectedRef = useRef(null);

    useEffect(() => {
        if (selectedRef.current && selectedRef.current.scrollIntoViewIfNeeded) {
            selectedRef.current.scrollIntoViewIfNeeded();
        }
    }, [selected]);

    useMousetrap('down', (e) => {
        e.preventDefault();
        if (selected === null) {
            setSelected(archers[0]);
        } else {
            const index = archers.indexOf(selected);
            if (index < archers.length - 1) {
                setSelected(archers[index + 1]);
            }
        }
    });

    useMousetrap('up', (e) => {
        e.preventDefault();
        if (selected !== null) {
            const index = archers.indexOf(selected);
            if (index > 0) {
                setSelected(archers[index - 1]);
            } else {
                setSelected(null);
            }
        }
    });

    useMousetrap('enter', (e) => {
        e.preventDefault();
        if (selected) {
            onSelect(selected);
        } else {
            close();
        }
    });

    const handleSearch = (e) => {
        const newSearch = e.target.value;
        setSearch(newSearch);
        const matchingArchers = archers.filter(archer => textMatcher(newSearch, archer.searchtext));
        if (newSearch === '') {
            setSelected(null);
        } else if (matchingArchers.length) {
            setSelected(matchingArchers[0]);
        } else {
            setSelected(null);
        }
    };

    const archerList = archers.filter(archer => textMatcher(search, archer.searchtext)).map(archer => {
        const clickHandler = (e) =>{
            e.preventDefault();
            onSelect(archer);
            close();
        }
        return (
            <li className="archer-selector__row" aria-selected={ selected === archer ? true : null } ref={ selected === archer ? selectedRef : null } key={ archer.id } onClick={ clickHandler }>
                { archer.name }
                <br />
                { archer.club }
                <br />
                <ArcherPills categories={ archer.categories } />
            </li>
        );
    });

    return (
        <div className="archer-selector" ref={ ref }>
            <input className="archer-selector__input mousetrap" value={ search } onChange={ handleSearch } autoFocus placeholder="Search by name, club, categories…" />
            <ul>
                { search === '' && <li className="archer-selector__row" aria-selected={ selected === null ? true : null } ref={ selected === null ? selectedRef : null } onClick={ close }>{ emptyLabel }</li> }
                { archerList }
            </ul>
        </div>
    );
};

export default ArcherSelector;
