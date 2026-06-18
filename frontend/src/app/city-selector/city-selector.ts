import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CITY_GROUPS, CityGroup } from './city-selector.constants';

@Component({
  selector: 'city-selector',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './city-selector.html',
  styleUrls: ['./city-selector.scss']
})
export class CitySelectorComponent {
  @Input() selectedValue?: string;
  @Output() selectionChange = new EventEmitter<string>();

  protected readonly cityGroups: CityGroup[] = CITY_GROUPS;

  protected onSelectChange(value: string): void {
    this.selectionChange.emit(value);
  }
}
