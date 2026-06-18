import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CITY_OPTIONS, CityOption } from './city-selector.constants';

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

  protected readonly cities: CityOption[] = CITY_OPTIONS;

  protected onSelectChange(value: string): void {
    this.selectionChange.emit(value);
  }
}
