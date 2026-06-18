import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CATEGORY_OPTIONS, CategoryOption } from './category-selector.constants';
import { isCategorySelected, toggleSelection } from '../utils/component-utils';

@Component({
  selector: 'category-selector',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './category-selector.html',
  styleUrls: ['./category-selector.scss']
})
export class CategorySelectorComponent {
  @Input() selectedValues: string[] = [];
  @Output() selectionChange = new EventEmitter<string[]>();

  protected readonly categories: CategoryOption[] = CATEGORY_OPTIONS;

  protected isSelected(value: string): boolean {
    return isCategorySelected(this.selectedValues, value);
  }

  protected onCheckboxChange(value: string, checked: boolean): void {
    const nextValues = toggleSelection(this.selectedValues, value, checked);

    this.selectionChange.emit(nextValues);
  }
}
